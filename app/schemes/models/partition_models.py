from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from app.schemes.base_models import KeywordSearchModel, SingleItemModel, PaginationModel


# 基础模型
class PartitionBase(BaseModel):
    partition_name: str


# 分区相关模型
class PartitionKeywordSearch(KeywordSearchModel):
    search_columns: List[str] = ["partition_name"]


class PartitionSingleItem(SingleItemModel):
    pass


class PartitionPagination(PaginationModel):
    pass


def get_partition(
        id: int
):
    return PartitionSingleItem(id=id)


def get_partitions(
        offset: int = 0,
        limit: int = 100
):
    return PartitionPagination(offset=offset, limit=limit)


class ResponsePartition(PartitionBase):
    id: int = None
    create_at: datetime | None = None
    update_at: datetime | None = None


class SearchPartitionResponse(ResponsePartition):
    rank_score: Optional[float] = None
    rank_position: Optional[int] = None


class PartitionCreate(PartitionBase):
    pass


class PartitionUpdate(BaseModel):
    id: int
    partition_name: Optional[str] = None
