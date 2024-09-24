from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemes.keyword_search import KeywordSearchModel


class FileBase(BaseModel):
    file_name: str
    file_hash: str = None
    partition_id: Optional[int] = None


class FileCreate(FileBase):
    pass


class FileUpdate(BaseModel):
    id: int
    file_name: Optional[str]


class FileKeywordSearch(KeywordSearchModel):
    id: Optional[int] = None
    column_name: str = "file_name"


class ResponseFile(BaseModel):
    id: int
    file_name: str
    reference_count: int
    create_at: datetime
    update_at: datetime
    partition_id: Optional[int] = None


class SearchFileResponse(ResponseFile):
    rank_score: Optional[float] = None
    rank_position: Optional[int] = None
