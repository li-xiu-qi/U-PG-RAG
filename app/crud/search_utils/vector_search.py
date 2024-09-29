from typing import List, Type
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.crud.search_utils.execute_query_utils import execute_query
from app.crud.filter_utils.filters import FilterHandler
from app.crud.search_utils.vector_search_utils import build_vector_search_query


async def vector_search(db: AsyncSession,
                        model: BaseModel,
                        filter_handler: FilterHandler) -> (
        List)[Type[DeclarativeBase]]:
    model_dict = model.model_dump(exclude_unset=True)
    query_vector = model_dict.pop('vector')
    offset = model_dict.pop('offset', 0)
    limit = model_dict.pop('limit', 20)
    filters = model_dict.pop('filters', {})
    threshold = model_dict.pop('threshold', None)

    filter_conditions = [filter_handler.create_filter_clause(filters)]
    query = build_vector_search_query(filter_handler.db_model, query_vector, filter_conditions, offset, limit,
                                      threshold)

    return await execute_query(db, query)
