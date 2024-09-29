"""
这里是一个将本地图片上传到远程服务器代码
传入一个本地图片路径，转化成webp格式上传到远程的minio，接着，返回一个远程图片路径
"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.crud.filter_utils.filters import FilterHandler
from app.crud.image_operation import ImageOperation
from app.db.db_models import File

bucket_name = "public-images"
image_operator = ImageOperation(filter_handler=FilterHandler(db_model=File),
                                bucket_name=bucket_name, public=True)


async def test():
    from config import ServeConfig

    engine = create_async_engine(ServeConfig.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        file_path = "/home/ke/桌面/my/RAG_project/U-PG-RAG/app/serves/file_processing/kelianxixi.jpg"
        image_url = await image_operator.local_img2remote(db, file_path)
        print(image_url)
        key = image_url.split("/")[-1]

        # res = await image_operator.image_map(key=key)
        # print(res.text)


if __name__ == "__main__":
    import asyncio

    asyncio.run(test())
