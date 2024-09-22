from typing import List, Type, TypeVar
from pydantic import BaseModel
from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.crud.execute_query_utils import execute_query
from app.crud.filter_utils.filters import FilterHandler

T = TypeVar('T', bound=BaseModel)


def sanitize_keywords(keywords: List[str]) -> List[str]:
    return [keyword.strip() for keyword in keywords if keyword.strip()]


def build_search_query(db_model: Type[DeclarativeBase], search_columns: List[str], query_condition: str, filters: dict,
                       sort_by_rank: bool, filter_handler: FilterHandler):
    search_vector = func.to_tsvector('jiebacfg',
                                     func.concat_ws(' ', *[getattr(db_model, col) for col in search_columns]))
    search_query = func.to_tsquery('jiebacfg', query_condition)
    search_condition = search_vector.op('@@')(search_query)

    query = select(db_model).where(search_condition)

    filter_clause = filter_handler.create_filter_clause(filters)
    query = query.where(filter_clause)

    if sort_by_rank:
        rank_score = func.ts_rank(search_vector, search_query).label('rank_score')
        rank_position = func.row_number().over(order_by=rank_score.desc()).label('rank_position')
        query = query.add_columns(*db_model.__table__.columns, rank_position, rank_score).order_by(rank_score.desc())
    else:
        query = query.add_columns(*db_model.__table__.columns)

    return query


async def search(db: AsyncSession, db_model: Type[DeclarativeBase], model: BaseModel, filter_handler: FilterHandler,
                 ) -> \
        List[Type[DeclarativeBase]]:
    model_dict = model.model_dump(exclude_unset=True)
    filters = model_dict.pop("filters", {})
    keywords = model_dict.pop("keywords", [])
    search_columns = model_dict.pop("search_columns", [])
    sort_by_rank = model_dict.pop("sort_by_rank", True)
    offset = model_dict.pop("offset", 0)
    limit = model_dict.pop("limit", 20)

    sanitized_keywords = sanitize_keywords(keywords)
    if not sanitized_keywords:
        return []

    if not search_columns:
        search_columns = [col.name for col in db_model.__table__.columns if col.name not in filter_handler.disallowed_fields]

    if not search_columns:
        return []

    query_condition = ' & '.join(sanitized_keywords)

    query = build_search_query(db_model, search_columns, query_condition, filters, sort_by_rank, filter_handler)
    query = query.offset(offset).limit(limit)

    return await execute_query(db, query)
