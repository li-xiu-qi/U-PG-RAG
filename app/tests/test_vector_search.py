from typing import List
from sqlalchemy import Column, Integer, String, Text, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase
from pgvector.sqlalchemy import VECTOR

from app.tests.config import DATABASE_URL
from helper.embedding import embedding
from app.crud.search_utils.vector_search import vector_search


class Base(DeclarativeBase):
    pass


class SampleData(BaseModel):
    vector: List[float]
    filters: dict | None = None


class DBSampleData(Base):
    __tablename__ = 'vector_data'
    doc_id = Column(Integer, primary_key=True)
    vector = Column(VECTOR)
    content = Column(Text)


engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


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
        {"doc_id": i + 1, "vector": embedding(content), "content": content}
        for i, content in enumerate(contents)
    ]

    for data in sample_data:
        record = DBSampleData(**data)
        session.add(record)

    await session.commit()


async def table_exists(session: AsyncSession, table_name: str) -> bool:
    result = await session.execute(
        text(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table_name}')")
    )
    return result.scalar()


# 异步主函数
async def main():
    async with AsyncSessionLocal() as session:
        if not await table_exists(session, 'vector_data'):
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)
            await insert_sample_data(session)

    # 执行向量检索
    async with AsyncSessionLocal() as session:
        input_content = "如何学习编程语言"
        search_model = SampleData(vector=embedding(input_content))
        results = await vector_search(session, DBSampleData, search_model)
        print("输入:", input_content)
        for res in results:
            print(res.doc_id, res.content, res.rank_position)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
