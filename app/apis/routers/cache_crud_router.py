from typing import Type, List, Optional, Dict, Callable

from fastapi import APIRouter
from pydantic import BaseModel

from app.apis.routers.base_crud_router import BaseCRUDRouter
from app.crud.base_operation import BaseOperation


class CacheCRUDRouter(BaseCRUDRouter):

    def __init__(
            self,
            router: APIRouter,
            operator: BaseOperation,
            response_model: Optional[Type[BaseModel]] = None,
            create_model: Optional[Type[BaseModel]] = None,
            update_model: Optional[Type[BaseModel]] = None,
            keyword_search_model: Optional[Type[BaseModel]] = None,
            search_response_model: Optional[Type[BaseModel]] = None,
            include_routes: Optional[Dict[str, bool]] = None,
    ):
        super().__init__(
            router=router,
            operator=operator,
            response_model=response_model,
            create_model=create_model,
            update_model=update_model,
            keyword_search_model=keyword_search_model,
            search_response_model=search_response_model,
            include_routes=include_routes
        )