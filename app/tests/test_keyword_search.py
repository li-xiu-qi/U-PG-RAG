import asyncio
import time
from typing import List

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from app.crud.search_utils import search
from app.tests.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)
Base = declarative_base()


class ExampleTable(Base):
    __tablename__ = 'example_keyword_table1'
    id = Column(Integer, primary_key=True)
    content = Column(String)

    def __repr__(self):
        return f"(id={self.id}, content={self.content})"


class KeywordModel(BaseModel):
    keywords: List[str] = []
    search_columns: List[str] = ["content"]
    sort_by_rank: bool = True
    offset: int = 0
    limit: int = 10
    exact_match: bool = False


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def insert_data(db: AsyncSession, data: List[dict]):
    for item in data:
        record = ExampleTable(**item)
        db.add(record)
    await db.commit()


async def main():
    async with AsyncSessionLocal() as session:
        await create_tables()

        contents = [
            "这是一辆拖拉机",
            "CEO 在会议上做出了重要决策",
            "农田里的拖拉机正在工作",
            "公司的 CEO 正在考虑新的战略",
            "决策过程需要仔细考虑"
        ]

        sample_data = [{"content": content} for content in contents]
        await insert_data(session, sample_data)

        allowed_columns = ["content"]

        queries = [
            (["拖拉机"], ["content"], True, "查询 '拖拉机' 的结果（允许的列，排序）"),
            (["拖拉机", "CEO"], ["content"], True, "查询 '拖拉机' 和 'CEO' 的结果（允许的列，排序）"),
            (["农田"], ["content"], False, "查询 '农田' 的结果（指定列，不排序）"),
            (["决策"], ["content"], True, "查询 '决策' 的结果（指定列，排序）"),
        ]

        start_time = time.time()
        for keywords, search_columns, sort_by_rank, description in queries:
            print(description)
            model = KeywordModel(
                keywords=keywords,
                search_columns=search_columns,
                sort_by_rank=sort_by_rank,
                exact_match=False
            )
            res = await search(session, ExampleTable, model, allowed_columns)
            for row in res:
                if sort_by_rank:
                    print(f"id: {row.id}, content: {row.content}, rank: {row.rank_position}")
                else:
                    print(f"id: {row.id}, content: {row.content}")
            print("\n")

        end_time = time.time()
        print("查询时间：", end_time - start_time)


if __name__ == "__main__":
    asyncio.run(main())