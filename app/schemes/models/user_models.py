from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from app.schemes.keyword_search import KeywordSearchModel


class ResponseToken(BaseModel):
    access_token: str
    token_type: str
    expires_at: datetime


class UserBase(BaseModel):
    name: str
    account: str
    email: Optional[str] = None
    phone: Optional[str] = None
    status: bool = True
    partition_id: Optional[int] = None


class UserCreate(UserBase):
    hashed_password: str


class UserUpdate(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    account: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[bool] = None
    partition_id: Optional[int] = None
    hashed_password: Optional[str] = None


class ResponseUser(UserBase):
    id: Optional[int] = None
    name: Optional[str] = None
    account: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[bool] = None
    partition_id: Optional[int] = None
    create_at: datetime | None = None
    update_at: datetime | None = None


class AdminBase(BaseModel):
    name: str
    account: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    status: bool = True
    school_id: Optional[int] = None


class AdminCreate(AdminBase):
    hashed_password: str


class AdminUpdate(BaseModel):
    name: Optional[str] = None
    account: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    status: Optional[bool] = None
    school_id: Optional[int] = None
    hashed_password: Optional[str] = None


class AdminKeywordSearch(KeywordSearchModel):
    search_columns: List[str] = ["school_name"]


class ResponseAdmin(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    account: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    status: Optional[bool] = None
    partition_id: Optional[int] = None
    create_at: datetime | None = None
    update_at: datetime | None = None


class SearchAdminResponse(ResponseAdmin):
    rank_score: Optional[float] = None
    rank_position: Optional[int] = None
