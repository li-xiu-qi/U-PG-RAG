import logging
import traceback
from typing import Optional, List

from fastapi import HTTPException, APIRouter, Depends, UploadFile, status
from minio import Minio
from sqlalchemy.ext.asyncio import AsyncSession

from app.apis.deps import get_db
from app.crud.file_operation import FileCRUD
from app.crud.file_utils.minio_service import MinIOFileService, generate_object_key
from app.schemes.model_filters import PartitionFilter
from app.schemes.models.file_models import FileResponse, FileSingleItem
from config import ServeConfig
from setup_app import init_minio_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
file_router = APIRouter(prefix="/files", tags=["文件处理"])


@file_router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=FileResponse)
async def upload_file(file: UploadFile, partition_id: Optional[int] = None, db: AsyncSession = Depends(get_db),
                      minio_client: Minio = Depends(init_minio_client)):
    try:
        minio_service = MinIOFileService(minio_client, ServeConfig.minio_bucket_name)
        file_crud = FileCRUD(db)
        file_content = await file.read()
        file_hash = generate_object_key(file_content)

        # 分区过滤
        partition_filter = PartitionFilter(partition_id=partition_id)
        existing_file = await file_crud.get_file_by_hash(file_hash, partition_filter)
        if existing_file:
            existing_file.reference_count += 1
            await file_crud.update_file(existing_file, {"reference_count": existing_file.reference_count})
            return existing_file
        else:
            file.file.seek(0)
            await minio_service.upload_file(file, file_hash)
            file_data = {"file_name": file.filename, "file_hash": file_hash, "partition_id": partition_id}
            new_file = await file_crud.create_file(file_data)
            return FileResponse(**new_file)
    except HTTPException as e:
        logger.error(f"HTTPException: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@file_router.get("/download/{file_id}", status_code=status.HTTP_200_OK)
async def download_file(file_id: int, partition_id: Optional[int] = None, db: AsyncSession = Depends(get_db),
                        minio_client: Minio = Depends(init_minio_client)):
    try:
        minio_service = MinIOFileService(minio_client, ServeConfig.minio_bucket_name)
        file_crud = FileCRUD(db)

        partition_filter = PartitionFilter(partition_id=partition_id)
        file = await file_crud.get_file(file_id, partition_filter)
        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        file_hash = file["file_hash"]
        download_url = await minio_service.generate_presigned_url(file_hash,
                                                                  expiry=ServeConfig.MINIO_DOWNLOAD_URL_EXPIRY)
        return {"download_url": download_url}
    except HTTPException as e:
        logger.error(f"HTTPException: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@file_router.delete("/delete/{file_id}", status_code=status.HTTP_200_OK)
async def delete_file(file_id: int, partition_id: Optional[int] = None, db: AsyncSession = Depends(get_db),
                      minio_client: Minio = Depends(init_minio_client)):
    try:
        minio_service = MinIOFileService(minio_client, ServeConfig.minio_bucket_name)
        file_crud = FileCRUD(db)

        partition_filter = PartitionFilter(partition_id=partition_id)
        file = await file_crud.get_file(file_id, partition_filter)
        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        file_hash = file["file_hash"]
        reference_count = file["reference_count"]

        if reference_count > 1:
            updated_file = await file_crud.update_file(file, {"reference_count": reference_count - 1})
            return {
                "detail": f"File '{file['file_name']}' still has {updated_file['reference_count']} references. File not deleted from MinIO."
            }
        else:
            await file_crud.delete_file(file_id, partition_filter)
            await minio_service.delete_file(file_hash)
            return {
                "detail": f"File '{file['file_name']}' successfully deleted from database and MinIO."
            }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")


@file_router.get("/download-multiple", status_code=status.HTTP_200_OK, response_model=List[FileSingleItem])
async def download_multiple_files(
        partition_id: Optional[int] = None,
        offset: int = 0,
        limit: int = 20,
        db: AsyncSession = Depends(get_db),
        minio_client: Minio = Depends(init_minio_client)
):
    try:
        minio_service = MinIOFileService(minio_client, ServeConfig.minio_bucket_name)
        file_crud = FileCRUD(db)

        partition_filter = PartitionFilter(partition_id=partition_id)
        files = await file_crud.get_multiple_files(partition_filter, offset, limit)

        if not files:
            raise HTTPException(status_code=404, detail="No files found")

        download_urls = []
        for file in files:
            file_hash = file.file_hash
            download_url = await minio_service.generate_presigned_url(file_hash,
                                                                      expiry=ServeConfig.MINIO_DOWNLOAD_URL_EXPIRY)
            download_urls.append(FileSingleItem(file_name=file.file_name, download_url=download_url))

        return download_urls
    except HTTPException as e:
        logger.error(f"HTTPException: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
