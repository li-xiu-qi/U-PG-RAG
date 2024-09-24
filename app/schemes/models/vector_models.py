from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from app.schemes.keyword_search import KeywordSearchModel


class VectorBase(BaseModel):
    page_content: str
    category: Optional[str] = None
    partition_id: Optional[int] = None
    file_id: Optional[int] = None
    md_id: Optional[int] = None
    doc_id: Optional[int] = None


class VectorCreate(VectorBase):
    pass


class VectorUpdate(BaseModel):
    id: int
    page_content: Optional[str] = None
    vector: Optional[List[float]] = None
    category: Optional[str] = None
    partition_id: Optional[int] = None
    file_id: Optional[int] = None
    md_id: Optional[int] = None
    doc_id: Optional[int] = None


class ResponseVector(BaseModel):
    id: int
    page_content: str
    category: Optional[str] = None
    partition_id: Optional[int] = None
    file_id: Optional[int] = None
    md_id: Optional[int] = None
    doc_id: Optional[int] = None
    create_at: datetime
    update_at: datetime


class VectorKeywordSearch(KeywordSearchModel):
    search_columns: List[str] = ["page_content"]


class SearchVectorResponse(BaseModel):
    id: int
    page_content: str
    category: Optional[str] = None
    partition_id: Optional[int] = None
    file_id: Optional[int] = None
    md_id: Optional[int] = None
    doc_id: Optional[int] = None
    create_at: datetime
    update_at: datetime
    rank_score: Optional[float] = None
    rank_position: Optional[int] = None


class VectorSearch(BaseModel):
    page_content: str
    offset: int = 0
    limit: int = 20
    vector: Optional[List[float]] = None


class HybridSearchModel(BaseModel):
    page_content: str
    keywords: List[str]
    search_columns: Optional[List[str]] = ["page_content"]
    sort_by_rank: Optional[bool] = True
    offset: Optional[int] = 0
    limit: Optional[int] = 20
    vector: Optional[List[float]] = None
    k: Optional[int] = 1


class SearchHybridResponse(BaseModel):
    id: int
    page_content: str
    category: Optional[str] = None
    partition_id: Optional[int] = None
    file_id: Optional[int] = None
    md_id: Optional[int] = None
    doc_id: Optional[int] = None
    create_at: datetime
    update_at: datetime
    rank_score: Optional[float] = None
    rank_position: Optional[int] = None
