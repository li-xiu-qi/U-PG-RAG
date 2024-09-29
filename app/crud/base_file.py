import hashlib

# import magic
from fastapi import HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base_operation import BaseOperation
from app.crud.file_utils.minio_service import MinIOFileService, init_minio_client
from app.crud.filter_utils.filters import FilterHandler


class BaseFile(BaseOperation):
    def __init__(self, filter_handler: FilterHandler,
                 bucket_name: str, public: bool = False):
        super().__init__(filter_handler)
        self.unique_keys = self.db_model.get_unique_columns()
        self.minio_client = init_minio_client()
        self.public = public
        self.bucket_name = bucket_name
        self.minio_service = MinIOFileService(minio_client=self.minio_client,
                                              bucket_name=bucket_name,
                                              public=public)

    async def create_file_item(self, *, db: AsyncSession, model: BaseModel, file: UploadFile):
        await file.seek(0)
        max_file_size = 50 * 1024 * 1024

        hash_sha256 = hashlib.sha256()
        file_content = b""
        while chunk := await file.read(1024 * 1024):
            file_content += chunk
            hash_sha256.update(chunk)
        file_size = len(file_content)
        if file_size > max_file_size:
            raise HTTPException(status_code=400, detail="File size exceeds the allowed limit.")

        file_hash = hash_sha256.hexdigest()
        if model is not None:
            model_dict = model.model_dump(exclude_unset=True)
        else:
            model_dict = {}
        model_dict["file_name"] = file.filename
        model_dict["file_size"] = file_size
        model_dict["content_type"] = file.content_type
        model_dict["file_hash"] = file_hash

        foreign_keys = {col.name: col for col in self.db_model.__table__.columns if col.foreign_keys}
        for fk_field, fk_column in foreign_keys.items():
            fk_value = model_dict.get(fk_field)
            if fk_value:
                fk_model = fk_column.foreign_keys.pop().column.table
                await self.db_model.check_foreign_key_exists(db, fk_model, fk_value)

        try:
            query = select(self.db_model).filter_by(file_hash=file_hash)
            result = await db.execute(query)
            existing_item = result.scalar_one_or_none()

            if existing_item:
                existing_item.reference_count += 1
                await db.commit()
                await db.refresh(existing_item)
                return existing_item

            db_item = self.db_model(**model_dict)
            db.add(db_item)
            await db.commit()
            await db.refresh(db_item)
            await file.seek(0)
            await self.minio_service.upload_file(file, file_hash)
            return db_item
        except Exception as e:
            await db.rollback()
            await self.minio_service.delete_file(file_hash)
            raise e

    async def generate_file_url(self, *, db: AsyncSession, _id: int, expiry: int | None):
        item = await self.get_item(db=db, _id=_id)
        return await self.minio_service.generate_file_url(item.file_hash, expiry)