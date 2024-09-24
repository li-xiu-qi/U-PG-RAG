from typing import List

from pydantic import BaseModel


class KeywordSearchModel(BaseModel):
    keywords: List[str]
    search_columns: List[str] = None
    sort_by_rank: bool
    offset: int
    limit: int
    filters: dict

