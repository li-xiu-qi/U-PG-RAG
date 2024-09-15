from typing import Type, List, Optional, Dict, Callable

from fastapi import APIRouter
from pydantic import BaseModel

from app.apis.routers.base_crud_router import BaseCRUDRouter
from app.crud.base_operation import BaseOperation


class DataCRUDRouter(BaseCRUDRouter):

    def __init__(
            self,
            router: APIRouter,
            dbmodel: type,
            response_model: Optional[Type[BaseModel]] = None,
            create_model: Optional[Type[BaseModel]] = None,
            update_model: Optional[Type[BaseModel]] = None,
            get_item: Optional[Callable] = None,
            get_items: Optional[Callable] = None,
            keyword_search_model: Optional[Type[BaseModel]] = None,
            search_response_model: Optional[Type[BaseModel]] = None,
            crud: Optional[Type[BaseOperation]] = None,
            unique_keys: Optional[List[str]] = None,
            allowed_columns: Optional[List[str]] = None,
            include_routes: Optional[Dict[str, bool]] = None,
    ):
        crud = crud or BaseOperation
        super().__init__(
            router=router,
            dbmodel=dbmodel,
            response_model=response_model,
            create_model=create_model,
            update_model=update_model,
            get_item=get_item,
            get_items=get_items,
            keyword_search_model=keyword_search_model,
            search_response_model=search_response_model,
            crud=crud,
            unique_keys=unique_keys,
            allowed_columns=allowed_columns,
            include_routes=include_routes
        )

    def setup_custom_routes(self):
        pass
