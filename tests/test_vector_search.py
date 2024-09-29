from typing import List

from pgvector.sqlalchemy import VECTOR
from pydantic import BaseModel
from sqlalchemy import Column, Integer, Text, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.crud.filter_utils.filters import FilterHandler
from app.crud.search_utils.vector_search import vector_search
from app.serves.model_serves.client_manager import ClientManager
from app.serves.model_serves.rag_model import RAGModel
from app.serves.model_serves.types import EmbeddingInput
from tests.config import ServeConfig
from diskcache import Cache

DATABASE_URL = ServeConfig.DATABASE_URL
async_embedding_cache = Cache("./cache")
embedding_client = ClientManager(api_configs=ServeConfig.embedding_api_configs)
embedding_rag = RAGModel(client_manager=embedding_client, cache=async_embedding_cache)


class Base(DeclarativeBase):
    pass


class SampleData(BaseModel):
    vector: List[float]
    filters: dict | list[dict] | None = None
    threshold: float | None = None


class DBSampleData(Base):
    __tablename__ = 'vector_data'
    doc_id = Column(Integer, primary_key=True)
    vector = Column(VECTOR)
    content = Column(Text)

    @classmethod
    def get_disallowed_columns(cls):
        return set()


engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def insert_sample_data(session: AsyncSession):
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

    sample_data = []
    for i, content in enumerate(contents):
        embedding_input = EmbeddingInput(name="BAAI/bge-m3", input_content=[content])
        vector_result = await embedding_rag.embedding(model_input=embedding_input)
        sample_data.append({
            "doc_id": i + 1,
            "vector": vector_result.output[0],
            "content": content
        })

    for data in sample_data:
        record = DBSampleData(**data)
        session.add(record)

    await session.commit()


async def table_exists(session: AsyncSession, table_name: str) -> bool:
    result = await session.execute(
        text(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table_name}')")
    )
    return result.scalar()


async def initialize_database():
    async with AsyncSessionLocal() as session:
        if not await table_exists(session, 'vector_data'):
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)
            await insert_sample_data(session)


async def perform_vector_search(session: AsyncSession, input_content: str, filters=None):
    embedding_input = EmbeddingInput(name="BAAI/bge-m3", input_content=[input_content])
    vector_result = await embedding_rag.embedding(model_input=embedding_input)
    search_model = SampleData(vector=vector_result.output[0], filters=filters, threshold=None)
    filter_handler = FilterHandler(
        db_model=DBSampleData,
    )
    results = await vector_search(session, search_model, filter_handler)
    return results


async def main():
    await initialize_database()

    async with AsyncSessionLocal() as session:
        input_content = "如何学习编程语言"
        results = await perform_vector_search(session, input_content)
        print("输入:", input_content)
        for res in results:
            print(res.doc_id, res.content, res.rank_position)

        # 测试用例2：带过滤条件
        # filters = {"content": {"not": [{"like": "%编程%"}, {"like": "%天气%"}]}}
        # filters = {"content": {"in": ["你的名字叫什么"]}}
        # filters = {"doc_id": {"between": [1, 10]}}
        # filters = {"content": {"exists": True}}
        filters = {"content": {"=": "你的名字叫什么"}}
        # filters = [{"content": {"like": "%编程%"}}, {"doc_id": {"in": [1, 2, 3]}}]
        results_with_filters = await perform_vector_search(session, input_content, filters=filters)
        print("输入:", input_content, "带过滤条件:", filters)
        for res in results_with_filters:
            print(res.doc_id, res.content, res.rank_position)


"""
"filters": [
    {
      "partition_name": {"or":[
        "like": "%1%",
        "like":"清华大学"
      ]}
    }
  ]
  
"filters": [
    {
      "partition_name": {"and":[
        "like": "%1%",
        "like":"1清华大学"
      ]}
    }
  ]
  
 "filters": [
    {
      "partition_name": {
        "like":"清华大学"
      }
    }
  ]
"""
if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
