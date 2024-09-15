from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from app.schemes.base_models import KeywordSearchModel, SingleItemModel, PaginationModel
from app.schemes.model_filters import UserFilter


# RAGCache相关模型
class RAGCacheBase(BaseModel):
    query: str
    response: str
    partition_id: Optional[int] = None
    user_id: Optional[int] = None
    expires_in: datetime
    is_valid: Optional[bool] = False


class RAGCacheCreate(RAGCacheBase):
    pass


class RAGCacheUpdate(BaseModel):
    id: int
    query: Optional[str] = None
    response: Optional[str] = None
    partition_id: Optional[int] = None
    user_id: Optional[int] = None
    expires_in: Optional[datetime] = None
    is_valid: Optional[bool] = None


class ResponseRAGCache(RAGCacheBase):
    id: int
    create_at: datetime
    update_at: datetime


class RAGCacheKeywordSearch(KeywordSearchModel):
    search_columns: List[str] = ["query", "response"]
    filters: Optional[UserFilter] = None


class RAGCacheSingleItem(SingleItemModel):
    filters: Optional[UserFilter] = None


class RAGCachePagination(PaginationModel):
    filters: Optional[UserFilter] = None


def get_rag_cache(id: int, partition_id: Optional[int] = None,
                  user_id: Optional[int] = None):
    filters = UserFilter(partition_id=partition_id, user_id=user_id)
    return RAGCacheSingleItem(id=id, filters=filters)


def get_rag_caches(offset: Optional[int] = 0, limit: Optional[int] = 20,
                   partition_id: Optional[int] = None,
                   user_id: Optional[int] = None):
    filters = UserFilter(partition_id=partition_id, user_id=user_id)
    return RAGCachePagination(offset=offset, limit=limit, filters=filters)


class SearchRAGCacheResponse(RAGCacheBase):
    id: int
    create_at: datetime
    update_at: datetime
    rank_score: Optional[float] = None
    rank_position: Optional[int] = None
