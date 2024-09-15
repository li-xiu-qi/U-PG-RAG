from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemes.base_models import KeywordSearchModel, SingleItemModel, PaginationModel
from app.schemes.model_filters import PartitionFilter


class FileBase(BaseModel):
    file_name: str
    file_hash: str
    partition_id: Optional[int] = None


class FileCreate(FileBase):
    pass


class FileUpdate(BaseModel):
    id: int
    file_name: Optional[str]
    filters: Optional[PartitionFilter] = None


class FileDelete(BaseModel):
    id: int
    filters: Optional[PartitionFilter] = None


class FileKeywordSearch(KeywordSearchModel):
    id: Optional[int] = None
    column_name: str = "file_name"
    filters: Optional[PartitionFilter] = None


class FileSingleItem(SingleItemModel):
    filters: Optional[PartitionFilter] = None


def get_file(
        id: int,
        partition_id: Optional[int] = None,
):
    filters = PartitionFilter(partition_id=partition_id)
    return FileSingleItem(id=id, filters=filters)


def get_files(
        offset: int | None = 0,
        limit: int | None = 20,
        partition_id: Optional[int] = None,
):
    filters = PartitionFilter(partition_id=partition_id)
    return FilePagination(offset=offset, limit=limit, filters=filters)


class FilePagination(PaginationModel):
    filters: Optional[PartitionFilter] = None


class FileResponse(BaseModel):
    id: int
    file_name: str
    create_at: datetime
    update_at: datetime
    partition_id: Optional[int] = None


class SearchFileResponse(BaseModel):
    id: int
    file_name: str
    create_at: datetime
    update_at: datetime
    rank_score: Optional[float] = None
    rank_position: Optional[int] = None
