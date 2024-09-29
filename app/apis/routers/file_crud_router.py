from typing import Optional, Type

from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.apis.deps import get_db
from app.apis.routers.base_crud_router import BaseCRUDRouter
from app.crud.file_operation import FileOperator
from config import ServeConfig


class FileCRUDRouter(BaseCRUDRouter):
    operator: FileOperator

    def __init__(
            self,
            router: APIRouter,
            operator: FileOperator,
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
        self._add_router("/data_process/", "post", self._default_data_process(), response_model=None)

    def _default_create_item(self):
        create_model = self.create_model  # Workaround to avoid using `self` in type hint

        async def create_file_item(file: UploadFile = File(...),
                                   model: create_model = Depends(),
                                   db: AsyncSession = Depends(get_db)):
            return await self.operator.create_file_item(db=db, model=model, file=file)

        return create_file_item

    def _default_generate_file_url(self):
        async def generate_file_url(_id: int, db: AsyncSession = Depends(get_db)):
            return await self.operator.generate_file_url(db=db, _id=_id,
                                                         expiry=ServeConfig.MINIO_DOWNLOAD_URL_EXPIRY)

        return generate_file_url

    def _default_data_process(self):
        async def data_process(partition_id: int, files: list[UploadFile],
                               remove_image_tag=True, db: AsyncSession = Depends(get_db), ):
            await self.operator.data_process(db=db, partition_id=partition_id, files=files,
                                             remove_image_tag=remove_image_tag)
            return {"message": "success"}

        return data_process
