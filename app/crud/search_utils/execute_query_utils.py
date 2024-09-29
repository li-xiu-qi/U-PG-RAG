from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


async def execute_query(db: AsyncSession, query):
    try:
        result = await db.execute(query)
        rows = result.all()
        return rows
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return []