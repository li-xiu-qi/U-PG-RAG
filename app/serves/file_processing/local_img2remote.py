"""
这里是一个将本地图片上传到远程服务器代码
传入一个本地图片路径，转化成webp格式上传到远程的minio，接着，返回一个远程图片路径
"""

import os

from PIL import Image
from fastapi import UploadFile

from app.crud.base_file import FileOperation
from app.crud.filter_utils.filters import FilterHandler
from app.db.db_models import File
from app.schemes.models.file_models import FileCreate

bucket_name = "public_image"
file_operator = FileOperation(filter_handler=FilterHandler(db_model=File),
                              bucket_name=bucket_name, public=True)


def convert_to_webp(input_path: str, output_path: str):
    with Image.open(input_path) as img:
        img.save(output_path, format="WEBP")


async def local_img2remote(db, file_path: str):
    webp_path = file_path.rsplit('.', 1)[0] + '.webp'
    convert_to_webp(file_path, webp_path)

    model = FileCreate(
        file_name=os.path.basename(webp_path),
    )

    with open(webp_path, "rb") as f:
        file = UploadFile(filename=webp_path, file=f)

        data_model = await file_operator.create_file_item(model=model, file=file, db=db)
        image_url = file_operator.minio_service.generate_file_url(db=db, _id=data_model.id)

    return image_url


async def test():
    from app.apis.deps import async_session

    async with async_session() as db:
        file_path = "kelianxixi.jpg"
        result = await local_img2remote(db, file_path)
        print(result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(test())
