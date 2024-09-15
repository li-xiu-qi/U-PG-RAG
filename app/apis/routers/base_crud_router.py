from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Callable, Type

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.apis.deps import get_db


class BaseCRUDRouter(ABC):
    default_include_routes = {
        "create": True,
        "read": True,
        "reads": True,
        "update": True,
        "delete": True,
        "search": True
    }

    def __init__(
            self,
            router: APIRouter,
            dbmodel: type,
            crud: Type[object],
            response_model: Optional[Type[BaseModel]] = None,
            create_model: Optional[Type[BaseModel]] = None,
            update_model: Optional[Type[BaseModel]] = None,
            get_item: Optional[Callable] = None,
            get_items: Optional[Callable] = None,
            keyword_search_model: Optional[Type[BaseModel]] = None,
            search_response_model: Optional[Type[BaseModel]] = None,
            unique_keys: Optional[List[str]] = None,
            allowed_columns: Optional[List[str]] = None,
            include_routes: Optional[Dict[str, bool]] = None,
    ):

        self.router = router
        self.dbmodel = dbmodel
        self.response_model = response_model
        self.create_model = create_model
        self.update_model = update_model
        self.get_item = get_item
        self.get_items = get_items
        self.keyword_search_model = keyword_search_model
        self.search_response_model = search_response_model
        self.crud = crud()
        self.unique_keys = unique_keys or []
        self.allowed_columns = allowed_columns or []
        self.include_routes = include_routes or self.default_include_routes
        self.route_map = {
            "create": self._default_create_route,
            "read": self._default_read_route,
            "reads": self._default_reads_router,
            "update": self._default_update_route,
            "delete": self._default_delete_route,
            "search": self._default_search_routes,
        }
        self.custom_route_map = None
        self.setup_routes()

    def setup_routes(self):
        self.route_map.update(self.custom_route_map or {})

        for route_name, route_func in self.route_map.items():
            if self.include_routes.get(route_name, True):
                route_func()
        self.setup_custom_routes()

    def _default_create_route(self):
        async def create(model: self.create_model, db: AsyncSession = Depends(get_db)):
            return await self.crud.create_item(db=db, dbmodel=self.dbmodel, model=model,
                                               unique_keys=self.unique_keys)

        self.router.post("/create_item/", response_model=self.response_model)(create)

    def _default_read_route(self):
        async def read(model: BaseModel = Depends(self.get_item),
                       db: AsyncSession = Depends(get_db)):
            return await self.crud.get_item(db=db, dbmodel=self.dbmodel, model=model)

        self.router.get("/read_item/", response_model=self.response_model)(read)

    def _default_reads_router(self):
        async def reads(model: BaseModel = Depends(self.get_items),
                        db: AsyncSession = Depends(get_db)):
            items = await self.crud.get_items(db=db, dbmodel=self.dbmodel, model=model)
            return items

        self.router.get("/read_items/", response_model=List[self.response_model])(reads)

    def _default_update_route(self):
        async def update(model: self.update_model, db: AsyncSession = Depends(get_db)):
            return await self.crud.update_item(db=db, dbmodel=self.dbmodel, model=model,
                                               unique_keys=self.unique_keys)

        self.router.put("/update_item/", response_model=self.response_model)(update)

    def _default_delete_route(self):
        async def delete(model: BaseModel = Depends(self.get_item),
                         db: AsyncSession = Depends(get_db)):
            return await self.crud.delete_item(db=db, dbmodel=self.dbmodel, model=model)

        self.router.delete("/delete_item/")(delete)

    def _default_search_routes(self):
        async def search(model: self.keyword_search_model, db: AsyncSession = Depends(get_db)):
            return await self.crud.search(db=db, dbmodel=self.dbmodel, model=model,
                                          allowed_columns=self.allowed_columns)

        self.router.post("/search/", response_model=List[self.search_response_model])(search)

    @abstractmethod
    def setup_custom_routes(self):
        pass
