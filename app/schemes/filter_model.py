from typing import Any, Optional, List, Dict, Union
from pydantic import BaseModel, Field


class FilterModel(BaseModel):
    offset: Optional[int] = 0
    limit: Optional[int] = 20
    filters: List[Dict[str, Union[Dict[str, Any]]]] = None


class ModelRead(BaseModel):
    id: int
    filters: List[Dict[str, Union[Dict[str, Any]]]] = None
