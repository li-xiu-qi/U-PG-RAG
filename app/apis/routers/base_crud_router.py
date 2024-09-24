from typing import List, Optional, Type
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.apis.deps import get_db
from app.crud.base_operation import BaseOperation
from app.schemes.filter_model import ModelRead, FilterModel


class BaseCRUDRouter:
    def __init__(
            self,
            router: APIRouter,
            operator: BaseOperation,
            response_model: Optional[Type[BaseModel]] = None,
            create_model: Optional[Type[BaseModel]] = None,
            read_model: Optional[Type[ModelRead]] = ModelRead,
            reads_model: Optional[Type[ModelRead]] = FilterModel,
            update_model: Optional[Type[BaseModel]] = None,
            keyword_search_model: Optional[Type[BaseModel]] = None,
            search_response_model: Optional[Type[BaseModel]] = None,
            include_routes: Optional[dict] = None,
    ):
        self.router = router
        self.operator = operator
        self.db_model = operator.db_model
        self.response_model = response_model
        self.create_model = create_model
        self.read_model = read_model
        self.reads_model = reads_model
        self.update_model = update_model
        self.keyword_search_model = keyword_search_model
        self.search_response_model = search_response_model

        self.default_include_routes = {
            "create": self.create_model is not None,
            "get": True,
            "gets": True,
            "read": True,
            "reads": True,
            "update": self.update_model is not None,
            "delete": True,
            "search": self.keyword_search_model is not None,
        }

        if include_routes is not None:
            self.include_routes = {key: include_routes.get(key, self.default_include_routes[key]) for key in
                                   self.default_include_routes}
        else:
            self.include_routes = self.default_include_routes
        self.setup_routes()

    def _add_router(self, path: str, method: str, endpoint, response_model=None):
        if method == "get":
            self.router.get(path, response_model=response_model)(endpoint)
        elif method == "post":
            self.router.post(path, response_model=response_model)(endpoint)
        elif method == "put":
            self.router.put(path, response_model=response_model)(endpoint)
        elif method == "delete":
            self.router.delete(path)(endpoint)

    def setup_routes(self):
        routes = {
            "get": ("/get_item/{_id}/", self._default_get_item(), self.response_model),
            "gets": ("/get_items/", self._default_get_items(), List[self.response_model]),
            "create": ("/create_item/", self._default_create_item(), self.response_model),
            "read": ("/read_item/", self._default_read_item(), self.response_model),
            "reads": ("/read_items/", self._default_read_items(), List[self.response_model]),
            "update": ("/update_item/", self._default_update_item(), self.response_model),
            "delete": ("/delete_item/{_id}/", self._default_delete_item(), None),
            "search": ("/search/", self._default_search_items(), List[self.search_response_model]),
        }

        method_map = {
            "get": "get",
            "gets": "get",
            "create": "post",
            "read": "post",
            "reads": "post",
            "update": "put",
            "delete": "delete",
            "search": "post",
        }

        for route, (path, endpoint, response_model) in routes.items():
            if self.include_routes.get(route, False):
                self._add_router(path, method_map[route], endpoint, response_model)

    def _default_get_item(self):
        async def get_item(_id: int, db: AsyncSession = Depends(get_db)):
            return await self.operator.get_item(db=db, _id=_id)

        return get_item

    def _default_get_items(self):
        async def get_items(offset: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
            return await self.operator.get_items(db=db, offset=offset, limit=limit)

        return get_items

    def _default_create_item(self):
        async def create_item(model: self.create_model, db: AsyncSession = Depends(get_db)):
            return await self.operator.create_item(db=db, model=model)

        return create_item

    def _default_read_item(self):
        async def read_item(model: self.read_model = Depends(), db: AsyncSession = Depends(get_db)):
            return await self.operator.read_item(db=db, model=model)

        return read_item

    def _default_read_items(self):
        async def read_items(model: self.reads_model, db: AsyncSession = Depends(get_db)):
            return await self.operator.read_items(db=db, model=model)

        return read_items

    def _default_update_item(self):
        async def update_item(model: self.update_model, db: AsyncSession = Depends(get_db)):
            return await self.operator.update_item(db=db, model=model)

        return update_item

    def _default_delete_item(self):
        async def delete_item(_id: int, db: AsyncSession = Depends(get_db)):
            return await self.operator.delete_item(db=db, _id=_id)

        return delete_item

    def _default_search_items(self):
        async def search_items(model: self.keyword_search_model, db: AsyncSession = Depends(get_db)):
            return await self.operator.search(db=db, model=model)

        return search_items