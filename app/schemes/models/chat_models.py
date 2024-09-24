from datetime import datetime
from typing import Optional, List, Dict, Union, Literal

from pydantic import BaseModel

from app.schemes.keyword_search import KeywordSearchModel


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


class ConversationKeywordSearch(KeywordSearchModel):
    search_columns: List[str] = ["messages"]


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


class ResponseRecordKeywordSearch(KeywordSearchModel):
    search_columns: List[str] = ["input", "response"]


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

