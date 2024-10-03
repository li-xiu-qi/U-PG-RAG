from datetime import datetime
from typing import Optional, List, Dict, Union, Any
from pydantic import BaseModel

from app.schemes.keyword_search import KeywordSearchModel


class ChunkBase(BaseModel):
    page_content: str
    vector: List[float] = None
    category: Optional[str] = None
    doc_metadata: Optional[Dict[str, Any]] = None
    partition_id: Optional[int] = None
    file_id: Optional[int] = None
    document_id: Optional[int] = None


class ChunkCreate(ChunkBase):
    pass


class ChunkUpdate(BaseModel):
    id: int
    page_content: Optional[str] = None
    vector: Optional[List[float]] = None
    doc_metadata: Optional[Dict[str, Any]] = None
    category: Optional[str] = None
    partition_id: Optional[int] = None
    file_id: Optional[int] = None
    document_id: Optional[int] = None


class ResponseChunk(BaseModel):
    id: int
    page_content: str
    category: Optional[str] = None
    doc_metadata: Optional[Dict[str, Any]] = None
    partition_id: Optional[int] = None
    file_id: Optional[int] = None
    document_id: Optional[int] = None
    create_at: datetime
    update_at: datetime


class ChunkKeywordSearch(KeywordSearchModel):
    search_columns: List[str] = ["page_content"]


class SearchChunkResponse(BaseModel):
    id: int
    page_content: str
    category: Optional[str] = None
    doc_metadata: Optional[Dict[str, Any]] = None
    partition_id: Optional[int] = None
    file_id: Optional[int] = None
    document_id: Optional[int] = None
    create_at: datetime
    update_at: datetime
    rank_score: Optional[float] = None
    rank_position: Optional[int] = None


class ChunkSearch(BaseModel):
    page_content: str
    offset: int = 0
    limit: int = 20
    vector: List[float] | None = None
    filters: List[Dict[str, Union[Dict[str, Any]]]] = None


class HybridSearchModel(BaseModel):
    page_content: str
    keywords: List[str]
    search_columns: Optional[List[str]] = ["page_content"]
    use_vector_search: bool = True
    use_keyword_search: bool = True
    rerank: bool = False
    sort_by_rank: Optional[bool] = True
    offset: Optional[int] = 0
    limit: Optional[int] = 20
    vector: List[float] | None = None
    k: Optional[int] = 1
    vector_weight: Optional[float] = 1.0
    keyword_weight: Optional[float] = 1.0
    paragraph_number_ranking: Optional[bool] = False
    filter_count: int | None = -1


class SearchHybridResponse(BaseModel):
    id: int
    page_content: str
    category: Optional[str] = None
    doc_metadata: Optional[Dict[str, Any]] = None
    partition_id: Optional[int] = None
    file_id: Optional[int] = None
    document_id: Optional[int] = None
    create_at: datetime
    update_at: datetime
    rank_score: Optional[float] = None
    rank_position: Optional[int] = None
