# 基础模型
from typing import List, Optional

from pydantic import BaseModel


class PaginationModel(BaseModel):
    offset: int = 0
    limit: int = 100
    filters: Optional[BaseModel] = None


class SingleItemModel(BaseModel):
    id: Optional[int] = None
    filters: Optional[BaseModel] = None


class KeywordSearchModel(BaseModel):
    keywords: List[str] = []
    search_columns: List[str] = []
    sort_by_rank: bool = True
    offset: int = 0
    limit: int = 20
    filters: Optional[BaseModel] = None
    exact_match: bool = False
