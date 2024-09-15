# 过滤器模型
from typing import Optional

from pydantic import BaseModel


class PartitionFilter(BaseModel):
    partition_id: Optional[int] = None


class FileFilter(PartitionFilter):
    file_id: Optional[int] = None


class MarkdownFilter(FileFilter):
    md_id: Optional[int] = None


class DocumentFilter(MarkdownFilter):
    doc_id: Optional[int] = None


class UserFilter(PartitionFilter):
    user_id: Optional[int] = None


class ConversationFilter(UserFilter):
    conversation_id: Optional[int] = None
