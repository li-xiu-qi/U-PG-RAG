import asyncio
import logging
import os

import aiofiles
from fastapi import UploadFile
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base_file import BaseFile
from app.crud.base_operation import BaseOperation
from app.crud.chunk_operation import ChunkOperation
from app.crud.file_utils.utils import sanitize_filename, generate_hash
from app.crud.filter_utils.filters import FilterHandler
from app.crud.image_operation import ImageOperation
from app.db.db_models import File, Chunk, Document, Image
from app.schemes.models.chunk_models import ChunkCreate
from app.schemes.models.document_models import DocumentCreate
from app.schemes.models.file_models import FileCreate
from app.serves.file_processing.file_convert import FileConvert
from app.serves.file_processing.split import nested_split_markdown
from tests.config import ServeConfig
from utils.find_root_dir import get_project_root

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class FileOperator(BaseFile):
    # TODO  加入事务维护数据一致性
    async def process_single_file(self, db: AsyncSession, partition_id: int, file: UploadFile,
                                  remove_image_tag=True) -> None:
        logger.info(f"Processing file: {file.filename}")
        file_model = FileCreate(partition_id=partition_id)
        try:
            file_data = await self.create_file_item(file=file, model=file_model, db=db)
            if file_data.reference_count > 1:
                logger.info(f"File {file.filename} is referenced multiple times, skipping processing.")
                return
            file_hash = file_data.file_hash

            work_dir = "/" + get_project_root(project_name="app", start_dir=__file__, stop_dir="U-PG-RAG")
            temp_dir_name = os.path.join(work_dir, "temp")
            dir_name = os.path.join(temp_dir_name, f"temp_{file_hash}")
            os.makedirs(dir_name, exist_ok=True)
            safe_file_name = sanitize_filename(os.path.basename(file_data.file_name))
            file_path = os.path.join(dir_name, safe_file_name)

            await file.seek(0)
            async with aiofiles.open(file_path, "wb") as f:
                while True:
                    chunk = await file.read(8192)
                    if not chunk:
                        break
                    await f.write(chunk)
            logger.info(f"File {file.filename} saved to {file_path}")

            convertor = FileConvert()
            md_content, new_file_path = convertor.convert(file_path)
            logger.info(f"File {file.filename} converted to Markdown")

            doc_hash_key = generate_hash(md_content)

            doc_operator = BaseOperation(filter_handler=FilterHandler(db_model=Document))
            doc_model = DocumentCreate(
                content=md_content,
                partition_id=partition_id,
                file_id=file_data.id,
                hash_key=doc_hash_key,
            )
            doc_data = await doc_operator.create_item(db=db, model=doc_model)
            logger.info(f"Document created for file {file.filename}")

            file_name = file_path.split('/')[-1]

            chunks = await nested_split_markdown(
                file_path=new_file_path, text=md_content, chunk_size=2000, metadata={"source": file_name},
                remove_image_tag=remove_image_tag, uri2remote=True,
                image_operator=ImageOperation(
                    filter_handler=FilterHandler(db_model=Image),
                    bucket_name=ServeConfig.minio_public_images_bucket_name,
                    public=True,
                ),
                db=db
            )
            logger.info(f"File {file.filename} split into chunks")

            chunk_operator = ChunkOperation(filter_handler=FilterHandler(db_model=Chunk))
            chunk_models = [
                ChunkCreate(
                    page_content=chunk.content_or_path,
                    doc_metadata=chunk.metadata,
                    partition_id=partition_id,
                    file_id=file_data.id,
                    document_id=doc_data.id,
                )
                for chunk in chunks
            ]

            await chunk_operator.filter_and_create_items(db=db, models=chunk_models)
            logger.info(f"Chunks saved for file {file.filename}")

        except (Exception, SQLAlchemyError) as e:
            logger.error(f"Error processing file {file.filename}: {e}")
            await db.rollback()
            raise

    async def data_process(self, db: AsyncSession, partition_id: int, files: list[UploadFile],
                           remove_image_tag=True) -> None:
        logger.info(f"Starting data processing for partition {partition_id}")
        try:
            tasks = [self.process_single_file(db, partition_id, file, remove_image_tag) for file in files]
            await asyncio.gather(*tasks)
            logger.info(f"Data processing completed for partition {partition_id}")
        except (Exception, SQLAlchemyError) as e:
            logger.error(f"Error processing data for partition {partition_id}: {e}")
            await db.rollback()
            raise
