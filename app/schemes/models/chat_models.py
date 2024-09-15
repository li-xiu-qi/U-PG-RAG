from datetime import datetime
from typing import Optional, List, Dict, Union, Literal

from pydantic import BaseModel

from app.schemes.base_models import KeywordSearchModel, SingleItemModel, PaginationModel
from app.schemes.model_filters import UserFilter, ConversationFilter


class Message(BaseModel):
    role: Union[Literal['user'], Literal['assistant'], Literal['system']]
    content: str


class ConversationBase(BaseModel):
    messages: List[Message]
    partition_id: Optional[int] = None
    user_id: Optional[int] = None


class ResponseRecordBase(BaseModel):
    input: str
    response: str
    partition_id: Optional[int] = None
    conversation_id: Optional[int] = None
    user_id: Optional[int] = None


# 会话相关模型
class ConversationKeywordSearch(KeywordSearchModel):
    search_columns: List[str] = ["messages"]
    filters: Optional[UserFilter] = None


class ConversationSingleItem(SingleItemModel):
    filters: Optional[UserFilter] = None


class ConversationPagination(PaginationModel):
    filters: Optional[UserFilter] = None


class SearchConversationResponse(ConversationBase):
    id: int
    create_at: datetime
    update_at: datetime
    rank_score: Optional[float] = None
    rank_position: Optional[int] = None


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(BaseModel):
    id: int
    messages: List[Message] = None
    partition_id: Optional[int] = None
    user_id: Optional[int] = None


class ResponseConversation(ConversationBase):
    id: int
    create_at: datetime
    update_at: datetime


# 响应记录相关模型
class ResponseRecordKeywordSearch(KeywordSearchModel):
    search_columns: List[str] = ["input", "response"]
    filters: Optional[ConversationFilter] = None


class ResponseRecordSingleItem(SingleItemModel):
    filters: Optional[ConversationFilter] = None


class ResponseRecordPagination(PaginationModel):
    filters: Optional[ConversationFilter] = None


class SearchResponseRecordResponse(ResponseRecordBase):
    id: int
    create_at: datetime
    update_at: datetime
    rank_score: Optional[float] = None
    rank_position: Optional[int] = None


class ResponseRecordCreate(ResponseRecordBase):
    pass


class ResponseRecordUpdate(BaseModel):
    id: int
    input: Optional[str] = None
    response: Optional[str] = None
    partition_id: Optional[int] = None
    conversation_id: Optional[int] = None
    user_id: Optional[int] = None


class ResponseResponseRecord(ResponseRecordBase):
    id: int
    create_at: datetime
    update_at: datetime


# 获取单个会话
def get_conversation(id: int, partition_id: Optional[int] = None, user_id: Optional[int] = None):
    filters = UserFilter(partition_id=partition_id, user_id=user_id)
    return ConversationSingleItem(id=id, filters=filters)


# 获取多个会话
def get_conversations(offset: int = 0, limit: int = 20, partition_id: Optional[int] = None,
                      user_id: Optional[int] = None):
    filters = UserFilter(partition_id=partition_id, user_id=user_id)
    return ConversationPagination(offset=offset, limit=limit, filters=filters)


# 获取单个响应记录
def get_response_record(id: int, partition_id: Optional[int] = None, conversation_id: Optional[int] = None,
                        user_id: Optional[int] = None):
    filters = ConversationFilter(partition_id=partition_id, conversation_id=conversation_id, user_id=user_id)
    return ResponseRecordSingleItem(id=id, filters=filters)


# 获取多个响应记录
def get_response_records(offset: int = 0, limit: int = 20, partition_id: Optional[int] = None,
                         conversation_id: Optional[int] = None, user_id: Optional[int] = None):
    filters = ConversationFilter(partition_id=partition_id, conversation_id=conversation_id, user_id=user_id)
    return ResponseRecordPagination(offset=offset, limit=limit, filters=filters)
