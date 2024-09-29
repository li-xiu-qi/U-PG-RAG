from typing import List, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.crud.search_utils.execute_query_utils import execute_query
from app.crud.filter_utils.filters import FilterHandler
from app.crud.search_utils.search_utils import build_search_query

T = TypeVar('T', bound=BaseModel)


def sanitize_keywords(keywords: List[str]) -> List[str]:
    return [keyword.strip() for keyword in keywords if keyword.strip()]


async def search(db: AsyncSession, model: BaseModel, filter_handler: FilterHandler,
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
        search_columns = [col.name for col in filter_handler.db_model.__table__.columns if
                          col.name not in filter_handler.disallowed_fields]

    if not search_columns:
        return []

    query_condition = ' & '.join(sanitized_keywords)

    query = build_search_query(filter_handler.db_model, search_columns, query_condition, filters, sort_by_rank,
                               filter_handler)
    query = query.offset(offset).limit(limit)

    return await execute_query(db, query)
