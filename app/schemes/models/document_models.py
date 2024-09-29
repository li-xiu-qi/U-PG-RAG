from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from app.schemes.keyword_search import KeywordSearchModel


# 基础模型
class DocumentBase(BaseModel):
    title: str | None = None
    content: str
    category: str | None = None
    hash_key: str | None = None
    partition_id: Optional[int] = None
    file_id: Optional[int] = None


class DocumentKeywordSearch(KeywordSearchModel):
    search_columns: List[str] = ["title", "content", "hash_key"]


class SearchDocumentResponse(DocumentBase):
    id: int
    create_at: datetime
    update_at: datetime
    rank_score: Optional[float] = None
    rank_position: Optional[int] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    id: int
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    hash_key: Optional[str] = None
    partition_id: Optional[int] = None


class ResponseDocument(DocumentBase):
    id: int
    create_at: datetime
    update_at: datetime
