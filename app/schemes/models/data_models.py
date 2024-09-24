from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from app.schemes.keyword_search import KeywordSearchModel


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


class DocumentKeywordSearch(KeywordSearchModel):
    search_columns: List[str] = ["title", "content", "hash_key"]


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
