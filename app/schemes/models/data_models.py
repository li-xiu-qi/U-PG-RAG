from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.schemes.base_models import KeywordSearchModel, SingleItemModel, PaginationModel
from app.schemes.model_filters import FileFilter, MarkdownFilter, DocumentFilter


# 基础模型
class ContentBase(BaseModel):
    title: str
    content: str
    category: str
    hash_key: str
    partition_id: Optional[int] = None
    file_id: Optional[int] = None


# Markdown 相关模型
class MarkdownKeywordSearch(KeywordSearchModel):
    search_columns: List[str] = ["title", "content", "hash_key"]
    filters: Optional[FileFilter] = None


class MarkdownSingleItem(SingleItemModel):
    filters: Optional[FileFilter] = None


class MarkdownPagination(PaginationModel):
    filters: Optional[FileFilter] = None


def get_markdown(
        id: int,
        file_id: Optional[int] = None,
        partition_id: Optional[int] = None,
):
    filters = FileFilter(
        file_id=file_id,
        partition_id=partition_id,
    )
    return MarkdownSingleItem(id=id, filters=filters)


def get_markdowns(
        offset: int | None = 0,
        limit: int | None = 20,
        file_id: Optional[int] = None,
        partition_id: Optional[int] = None, ):
    filters = FileFilter(file_id=file_id, partition_id=partition_id)
    return MarkdownPagination(offset=offset, limit=limit, filters=filters)


class MarkdownBase(ContentBase):
    file_id: Optional[int] = None


class SearchMarkdownResponse(MarkdownBase):
    id: int
    create_at: datetime
    update_at: datetime
    rank_score: Optional[float] = None
    rank_position: Optional[int] = None


class MarkdownCreate(MarkdownBase):
    pass


class MarkdownUpdate(BaseModel):
    id: int
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    hash_key: Optional[str] = None
    partition_id: Optional[int] = None
    file_id: Optional[int] = None


class ResponseMarkdown(MarkdownBase):
    id: int
    create_at: datetime
    update_at: datetime


# 文档相关模型
class DocumentKeywordSearch(KeywordSearchModel):
    search_columns: List[str] = ["title", "content", "hash_key"]
    filters: Optional[MarkdownFilter] = None


class DocumentSingleItem(SingleItemModel):
    filters: Optional[MarkdownFilter] = None


class DocumentPagination(PaginationModel):
    filters: Optional[MarkdownFilter] = None


def get_document(id: int,
                 file_id: Optional[int] = None,
                 md_id: Optional[int] = None,
                 partition_id: Optional[int] = None, ):
    filters = MarkdownFilter(file_id=file_id,
                             md_id=md_id,
                             partition_id=partition_id)
    return DocumentSingleItem(id=id, filters=filters)


def get_documents(offset: int | None = 0,
                  limit: int | None = 20,
                  file_id: Optional[int] = None,
                  md_id: Optional[int] = None,
                  partition_id: Optional[int] = None, ):
    filters = MarkdownFilter(file_id=file_id,
                             md_id=md_id, partition_id=partition_id)
    return DocumentPagination(offset=offset, limit=limit, filters=filters)


class DocumentBase(ContentBase):
    markdown_id: Optional[int] = None


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
    hash_key: Optional[str] = None
    partition_id: Optional[int] = None
    markdown_id: Optional[int] = None


class ResponseDocument(DocumentBase):
    id: int
    create_at: datetime
    update_at: datetime
