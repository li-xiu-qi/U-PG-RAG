from fastapi import HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base_operation import BaseOperation
from app.crud.file_utils.minio_service import MinIOFileService, generate_object_key, init_minio_client
from app.crud.filter_utils.filters import FilterHandler


class FileOperation(BaseOperation):
    def __init__(self, filter_handler: FilterHandler, bucket_name: str):
        super().__init__(filter_handler)
        self.unique_keys = self.db_model.get_unique_columns()
        self.minio_client = init_minio_client()
        self.minio_service = MinIOFileService(self.minio_client, bucket_name)

    async def create_file_item(self, *, db: AsyncSession, model: BaseModel, file: UploadFile):
        model_dict = model.model_dump(exclude_unset=True)
        if not model_dict.get("file_hash"):
            object_key = generate_object_key(await file.read())
        else:
            object_key = model_dict.get("file_hash")

        if self.unique_keys:
            conflict_filters = {key: model_dict[key] for key in self.unique_keys if key in model_dict}
            query = select(self.db_model).filter_by(**conflict_filters)
            result = await db.execute(query)
            existing_item = result.scalar_one_or_none()

            if existing_item:
                raise HTTPException(status_code=409,
                                    detail=f"Conflict detected: The item with {conflict_filters} already exists.")

        db_item = self.db_model(**model_dict)
        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)

        await self.minio_service.upload_file(file, object_key)
        return db_item

    async def delete_file_item(self, *, db: AsyncSession, _id: int):
        item = await self.get_item(db=db, _id=_id)
        await self.minio_service.delete_file(item.object_key)
        await db.delete(item)
        await db.commit()
        return item

    async def generate_file_url(self, *, db: AsyncSession, _id: int, expiry: int):
        item = await self.get_item(db=db, _id=_id)
        return await self.minio_service.generate_file_url(item.file_hash, expiry)
