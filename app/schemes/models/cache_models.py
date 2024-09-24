from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from app.schemes.keyword_search import KeywordSearchModel


# RAGCache相关模型
class RAGCacheBase(BaseModel):
    query: str
    response: str
    partition_id: Optional[int] = None
    user_id: Optional[int] = None
    expires_in: Optional[datetime] = None
    is_valid: Optional[bool] = False


class RAGCacheCreate(RAGCacheBase):
    pass


class RAGCacheUpdate(RAGCacheBase):
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


class SearchRAGCacheResponse(RAGCacheBase):
    id: int
    create_at: datetime
    update_at: datetime
    rank_score: Optional[float] = None
    rank_position: Optional[int] = None
