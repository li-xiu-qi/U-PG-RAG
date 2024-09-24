from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from app.schemes.keyword_search import KeywordSearchModel


class PartitionBase(BaseModel):
    partition_name: str


class ResponsePartition(PartitionBase):
    id: int = None
    create_at: datetime | None = None
    update_at: datetime | None = None


class PartitionKeywordSearch(KeywordSearchModel):
    search_columns: List[str] = ["partition_name"]


class SearchPartitionResponse(ResponsePartition):
    rank_score: Optional[float] = None
    rank_position: Optional[int] = None


class PartitionCreate(PartitionBase):
    pass


class PartitionUpdate(BaseModel):
    id: int
    partition_name: Optional[str] = None
