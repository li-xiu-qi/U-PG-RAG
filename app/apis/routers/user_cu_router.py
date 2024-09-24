from typing import Callable, Optional, List, Type, Dict

from fastapi import APIRouter, Depends, Form
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.apis.deps import get_db
from app.apis.routers.base_auth_router import BaseAuthRouter
from app.crud.user_operation import UserOperation


class UserCURouter(BaseAuthRouter):
    operator: UserOperation

    def __init__(self,
                 router: APIRouter,
                 operator: UserOperation,
                 response_model: Optional[Type[BaseModel]] = None,
                 create_model: Optional[Type[BaseModel]] = None,
                 update_model: Optional[Type[BaseModel]] = None,
                 keyword_search_model: Optional[Type[BaseModel]] = None,
                 search_response_model: Optional[Type[BaseModel]] = None,
                 include_routes: Optional[Dict[str, bool]] = None,
                 ):
        user_include_routes = {
            "create": True,
            "update": True,
            "delete": False,
            "get": False,
            "gets": False,
            "read": False,
            "reads": False,
            "search": False,
            "keyword_search": False
        }
        super().__init__(
            router=router,
            operator=operator,
            response_model=response_model,
            create_model=create_model,
            update_model=update_model,
            keyword_search_model=keyword_search_model,
            search_response_model=search_response_model,
            include_routes=include_routes if include_routes else user_include_routes
        )

    def _default_create_route(self):
        @self.router.post("/create_item/", response_model=self.response_model)
        async def create(
                name: str = Form(...),
                account: str = Form(...),
                email: Optional[str] = Form(None),
                phone: Optional[str] = Form(None),
                partition_id: Optional[int] = Form(None),
                hashed_password: str = Form(...),
                db: AsyncSession = Depends(get_db)
        ):
            model = self.create_model(
                name=name,
                account=account,
                email=email,
                phone=phone,
                status=True,
                partition_id=partition_id,
                hashed_password=hashed_password
            )
            return await self.operator.create_item(db=db, model=model)

    def _default_update_route(self):
        @self.router.put("/update_item/", response_model=self.response_model)
        async def update(
                id: int = Form(...),
                name: Optional[str] = Form(None),
                account: Optional[str] = Form(None),
                email: Optional[str] = Form(None),
                phone: Optional[str] = Form(None),
                partition_id: Optional[int] = Form(None),
                hashed_password: Optional[str] = Form(None),
                db: AsyncSession = Depends(get_db)
        ):
            model = self.update_model(
                id=id,
                name=name,
                account=account,
                email=email,
                phone=phone,
                partition_id=partition_id,
                hashed_password=hashed_password
            )
            return await self.operator.update_item(db=db, model=model)
