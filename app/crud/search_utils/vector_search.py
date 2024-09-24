from typing import List, Type
from pydantic import BaseModel
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.crud.execute_query_utils import execute_query
from app.crud.filter_utils.filters import FilterHandler


def build_vector_search_query(db_model: Type[DeclarativeBase], query_vector,
                              filter_conditions: list, offset: int,
                              limit: int, threshold: float = None):
    columns_to_select = [col for col in db_model.__table__.columns if col.name != 'vector']
    query = select(db_model).add_columns(*columns_to_select)

    if filter_conditions:
        query = query.where(and_(*filter_conditions))

    similarity_score = db_model.vector.op('<=>')(query_vector)
    rank_position = func.row_number().over(order_by=similarity_score.asc()).label('rank_position')
    query = query.add_columns(rank_position).order_by(rank_position).offset(offset).limit(limit)

    if threshold is not None:
        query = query.where(similarity_score >= threshold)

    return query


async def vector_search(db: AsyncSession,
                        model: BaseModel, filter_handler: FilterHandler) -> List[
    Type[DeclarativeBase]]:
    model_dict = model.model_dump(exclude_unset=True)
    query_vector = model_dict.pop('vector')
    offset = model_dict.pop('offset', 0)
    limit = model_dict.pop('limit', 20)
    filters = model_dict.pop('filters', {})
    threshold = model_dict.pop('threshold')

    filter_conditions = [filter_handler.create_filter_clause(filters)]
    query = build_vector_search_query(filter_handler.db_model, query_vector, filter_conditions, offset, limit,
                                      threshold)

    return await execute_query(db, query)
