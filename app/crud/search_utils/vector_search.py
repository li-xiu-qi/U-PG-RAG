from typing import List, Type
from pydantic import BaseModel
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import SQLAlchemyError


def extract_model_dict(model: BaseModel) -> dict:
    return model.model_dump(exclude_unset=True)


def build_filter_conditions(db_model: Type[DeclarativeBase], filters: dict) -> list:
    return [getattr(db_model, key) == value for key, value in filters.items()]


def build_vector_search_query(db_model: Type[DeclarativeBase], query_vector, filter_conditions: list, offset: int,
                              limit: int):
    columns_to_select = [col for col in db_model.__table__.columns if col.name != 'vector']
    query = select(db_model).add_columns(*columns_to_select)

    if filter_conditions:
        query = query.where(and_(*filter_conditions))

    rank_position = func.row_number().over(order_by=db_model.vector.op('<=>')(query_vector).asc()).label(
        'rank_position')
    query = query.add_columns(rank_position).order_by(rank_position).offset(offset).limit(limit)

    return query


async def execute_query(db: AsyncSession, query):
    try:
        result = await db.execute(query)
        return result.all()
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return []


async def vector_search(db: AsyncSession, db_model: Type[DeclarativeBase],
                        model: BaseModel) -> List[Type[DeclarativeBase]]:
    model_dict = extract_model_dict(model)
    query_vector = model_dict.pop('vector')
    offset = model_dict.pop('offset', 0)
    limit = model_dict.pop('limit', 20)
    filters = model_dict.pop('filters', {})

    filter_conditions = build_filter_conditions(db_model, filters)
    query = build_vector_search_query(db_model, query_vector, filter_conditions, offset, limit)

    return await execute_query(db, query)
