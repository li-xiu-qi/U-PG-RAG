from typing import List, Dict, Union, Any

from pydantic import BaseModel


class KeywordSearchModel(BaseModel):
    keywords: List[str]
    search_columns: List[str] = None
    sort_by_rank: bool
    offset: int = 0
    limit: int = 10
    filters: List[Dict[str, Union[Dict[str, Any]]]] = None

