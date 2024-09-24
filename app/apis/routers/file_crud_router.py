from fastapi import APIRouter, Depends, UploadFile, Form
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Type, List

from app.apis.deps import get_db
from app.crud.file_operation import FileOperation
from app.apis.routers.base_crud_router import BaseCRUDRouter
from app.tests.config import ServeConfig


class FileCRUDRouter(BaseCRUDRouter):
    operator: FileOperation

    def __init__(
            self,
            router: APIRouter,
            operator: FileOperation,
            create_model: Optional[Type[BaseModel]] = None,
            update_model: Optional[Type[BaseModel]] = None,
            response_model: Optional[Type[BaseModel]] = None,
            keyword_search_model: Optional[Type[BaseModel]] = None,
            search_response_model: Optional[Type[BaseModel]] = None,
            include_routes: Optional[dict] = None,
    ):
        super().__init__(
            router=router,
            operator=operator,
            response_model=response_model,
            create_model=create_model,
            update_model=update_model,
            keyword_search_model=keyword_search_model,
            search_response_model=search_response_model,
            include_routes=include_routes,
        )

    def setup_routes(self):
        super().setup_routes()
        self._add_router("/generate_url/{_id}/", "get", self._default_generate_file_url(), str)

    def _default_create_item(self):
        async def create_file_item(file: UploadFile, model: self.create_model = Depends(),
                                   db: AsyncSession = Depends(get_db)):
            print(f"model:", model)

            return await self.operator.create_file_item(db=db, model=model, file=file)

        return create_file_item

    def _default_generate_file_url(self):
        async def generate_file_url(_id: int, db: AsyncSession = Depends(get_db)):
            return await self.operator.generate_file_url(db=db, _id=_id, expiry=ServeConfig.MINIO_DOWNLOAD_URL_EXPIRY)

        return generate_file_url
