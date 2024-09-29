from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemes.keyword_search import KeywordSearchModel


class FileBase(BaseModel):
    partition_id: int | None = None


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
    file_name: str | None
    reference_count: int | None
    file_size: int | None
    content_type: str | None
    is_convert: bool | None
    create_at: datetime
    update_at: datetime
    partition_id: Optional[int] = None


class SearchFileResponse(ResponseFile):
    rank_score: Optional[float] = None
    rank_position: Optional[int] = None


class DbFile(BaseModel):
    file_name: str
    file_size: int
    content_type: str
    is_convert: bool
    file_hash: str
    partition_id: Optional[int] = None
