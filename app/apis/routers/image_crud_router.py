from io import BytesIO
from typing import Optional, Type

from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from app.apis.routers.file_crud_router import FileCRUDRouter
from app.crud.image_operation import ImageOperation


class ImageCRUDRouter(FileCRUDRouter):
    operator: ImageOperation

    def __init__(
            self,
            router: APIRouter,
            operator: ImageOperation,
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
        self._add_router("/{key}/", "get", self._default_public_images(), bytes)

    def _default_public_images(self):
        async def generate_public_images(key: str):
            image_data = await self.operator.image_map(key)
            return StreamingResponse(BytesIO(image_data), media_type="image/webp")

        return generate_public_images
