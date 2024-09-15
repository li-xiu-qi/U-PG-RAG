from typing import Type, List, Optional, Dict, Callable
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.apis.deps import get_db
from app.apis.routers.base_crud_router import BaseCRUDRouter
from app.crud.vector_operation import VectorOperation


class VectorRouter(BaseCRUDRouter):
    def __init__(
            self,
            router: APIRouter,
            dbmodel: Type,
            response_model: Optional[Type[BaseModel]] = None,
            create_model: Optional[Type[BaseModel]] = None,
            update_model: Optional[Type[BaseModel]] = None,
            get_item: Optional[Callable] = None,
            get_items: Optional[Callable] = None,
            keyword_search_model: Optional[Type[BaseModel]] = None,
            search_response_model: Optional[Type[BaseModel]] = None,
            vector_search_model: Optional[Type[BaseModel]] = None,
            hybrid_search_model: Optional[Type[BaseModel]] = None,
            crud: Optional[Type[VectorOperation]] = None,
            unique_keys: Optional[List[str]] = None,
            allowed_columns: Optional[List[str]] = None,
            include_routes: Optional[Dict[str, bool]] = None,
    ):
        self.vector_search_model = vector_search_model
        self.hybrid_search_model = hybrid_search_model
        self.search_response_model = search_response_model
        super().__init__(
            router=router,
            dbmodel=dbmodel,
            crud=crud or VectorOperation,
            response_model=response_model,
            create_model=create_model,
            update_model=update_model,
            get_item=get_item,
            get_items=get_items,
            keyword_search_model=keyword_search_model,
            search_response_model=search_response_model,
            unique_keys=unique_keys,
            allowed_columns=allowed_columns,
            include_routes=include_routes
        )

    def setup_custom_routes(self):
        """设置路由"""
        super().setup_custom_routes()

        if self.include_routes.get("vector_search", True):
            self._default_vector_search_route()
        if self.include_routes.get("hybrid_search", True):
            self._default_hybrid_search_route()

    def _default_vector_search_route(self):
        """设置默认的向量搜索路由"""

        @self.router.post("/vector_search/", response_model=List[self.search_response_model])
        async def vector_search(
                model: self.vector_search_model,
                db: AsyncSession = Depends(get_db),
        ):
            return await self.crud.vector_search(
                db=db,
                dbmodel=self.dbmodel,
                model=model
            )

    def _default_hybrid_search_route(self):
        """设置默认的混合搜索路由"""

        @self.router.post("/hybrid_search/", response_model=List[self.search_response_model])
        async def hybrid_search(
                model: self.hybrid_search_model,
                db: AsyncSession = Depends(get_db)
        ):
            return await self.crud.hybrid_search(
                db=db,
                dbmodel=self.dbmodel,
                model=model,
                allowed_columns=self.allowed_columns
            )
