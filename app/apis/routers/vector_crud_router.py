from typing import Type, List, Optional, Dict, Callable
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.apis.deps import get_db
from app.apis.routers.base_crud_router import BaseCRUDRouter
from app.crud.vector_operation import VectorOperation


class VectorRouter(BaseCRUDRouter):
    operator: VectorOperation

    def __init__(
            self,
            router: APIRouter,
            operator: VectorOperation,
            response_model: Optional[Type[BaseModel]] = None,
            create_model: Optional[Type[BaseModel]] = None,
            update_model: Optional[Type[BaseModel]] = None,
            keyword_search_model: Optional[Type[BaseModel]] = None,
            search_response_model: Optional[Type[BaseModel]] = None,
            vector_search_model: Optional[Type[BaseModel]] = None,
            hybrid_search_model: Optional[Type[BaseModel]] = None,
            include_routes: Optional[Dict[str, bool]] = None,
    ):
        self.vector_search_model = vector_search_model
        self.hybrid_search_model = hybrid_search_model
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

    def setup_routes(self):
        super().setup_routes()
        self._default_vector_search_route()
        self._default_hybrid_search_route()

    def _default_vector_search_route(self):
        @self.router.post("/vector_search/", response_model=List[self.search_response_model])
        async def vector_search(
                model: self.vector_search_model,
                db: AsyncSession = Depends(get_db),
        ):
            return await self.operator.vector_search(
                db=db,
                model=model
            )

    def _default_hybrid_search_route(self):
        @self.router.post("/hybrid_search/", response_model=List[self.search_response_model])
        async def hybrid_search(
                model: self.hybrid_search_model,
                db: AsyncSession = Depends(get_db)
        ):
            return await self.operator.hybrid_search(
                db=db,
                model=model
            )
