import aiohttp
# import magic
from PIL import Image
from fastapi import UploadFile
from pydantic import BaseModel

from app.crud.base_file import BaseFile
from config import ServeConfig

import hashlib
from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


class ImageOperation(BaseFile):
    async def local_img2remote(self, db: AsyncSession, file_path: str, model: BaseModel = None):
        if not self.public:
            raise Exception("This operation is only allowed for public files.")

        webp_path = file_path.rsplit('.', 1)[0] + '.webp'
        convert_to_webp(file_path, webp_path)

        with open(webp_path, "rb") as f:
            file = UploadFile(filename=webp_path, file=f)

            data_model = await self.create_file_item(model=model, file=file, db=db)
            obj_key = data_model.image_hash
            image_url = await self.minio_service.generate_file_url(obj_key)
            image_key = image_url.split("/")[-1]
            image_url = f"{ServeConfig.server_host}/{self.bucket_name}/{image_key}"

        return image_url

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
        image_hash = hash_sha256.hexdigest()
        if model is not None:
            model_dict = model.model_dump(exclude_unset=True)
        else:
            model_dict = {}
        model_dict["image_name"] = file.filename
        model_dict["image_size"] = file_size
        model_dict["image_hash"] = image_hash

        # Check for foreign key existence
        foreign_keys = {col.name: col for col in self.db_model.__table__.columns if col.foreign_keys}
        for fk_field, fk_column in foreign_keys.items():
            fk_value = model_dict.get(fk_field)
            if fk_value:
                fk_model = fk_column.foreign_keys.pop().column.table
                await self.db_model.check_foreign_key_exists(db, fk_model, fk_value)

        try:
            query = select(self.db_model).filter_by(image_hash=image_hash)
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
            await self.minio_service.upload_file(file, image_hash)
            return db_item
        except Exception as e:
            await db.rollback()
            await self.minio_service.delete_file(image_hash)
            raise e

    async def image_map(self, key: str):
        url = f"http://{ServeConfig.minio_endpoint}/{self.bucket_name}/{key}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    response.raise_for_status()


def convert_to_webp(input_path: str, output_path: str):
    with Image.open(input_path) as img:
        img.save(output_path, format="WEBP")
