from typing import List

from pgvector.sqlalchemy import VECTOR
from pydantic import BaseModel
from sqlalchemy import Column, Integer, Text
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.crud.search_utils import hybrid_search
from tests.test_keyword_search import DATABASE_URL
from helper.embedding import embedding


# 定义数据库模型基类
class Base(DeclarativeBase):
    pass


# 定义 Pydantic 模型
class HybridSampleData(BaseModel):
    vector: List[float]
    filters: dict | None = None
    keywords: List[str] | None = None
    search_columns: List[str] | None = None
    sort_by_rank: bool | None = True
    offset: int | None = 0
    limit: int | None = 20
    exact_match: bool = False


class DBHybridSampleData(Base):
    __tablename__ = 'hybrid_sample_data'

    id = Column(Integer, primary_key=True)
    vector = Column(VECTOR)
    content = Column(Text)


engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# 异步插入示例数据
async def insert_sample_data(session: AsyncSession):
    # 定义内容列表
    contents = [
        "你的名字叫什么",
        "如何学习Python编程",
        "今天天气真好",
        "如何提高英语听力",
        "中国历史概述",
        "最新科技新闻",
        "健康饮食小贴士",
        "旅游推荐：云南大理",
        "经济数据分析",
        "文学作品欣赏",
        "环境保护倡议",
        "量子计算机发展现状",
        "新能源汽车市场趋势",
        "5G技术与应用",
        "人工智能未来展望"
    ]

    # 创建sample_data
    sample_data = [
        {"id": i + 1, "vector": embedding(content), "content": content}
        for i, content in enumerate(contents)
    ]

    for data in sample_data:
        record = DBHybridSampleData(**data)
        session.add(record)

    await session.commit()


# 异步主函数
async def main():
    await drop_tables()
    await create_tables()

    async with AsyncSessionLocal() as session:
        await insert_sample_data(session)

    # 执行混合检索
    async with AsyncSessionLocal() as session:
        input_content = "学习编程"
        search_model = HybridSampleData(
            vector=embedding(input_content),
            keywords=["学习", "编程"],
            search_columns=["content"],
            sort_by_rank=True,
            offset=0,
            limit=10,
            exact_match=False
        )
        allowed_columns = ["content"]
        results = await hybrid_search(session, DBHybridSampleData, search_model, allowed_columns)
        print("输入:", input_content)
        for res in results:
            print(res.id, res.content)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
