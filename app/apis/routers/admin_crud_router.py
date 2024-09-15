from typing import Callable, Optional, List, Type, Dict

from fastapi import APIRouter, Depends, Form, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.apis.deps import get_db
from app.apis.routers.base_auth_router import BaseAuthRouter
from app.core.auth import get_admin_user
from app.crud.admin_operation import AdminOperation
from app.schemes.models.user_models import ResponseAdmin


class AdminCRUDRouter(BaseAuthRouter):

    def __init__(self,
                 router: APIRouter,
                 dbmodel: type,
                 response_model: Optional[Type[BaseModel]] = None,
                 create_model: Optional[Type[BaseModel]] = None,
                 update_model: Optional[Type[BaseModel]] = None,
                 get_item: Optional[Callable] = None,
                 get_items: Optional[Callable] = None,
                 keyword_search_model: Optional[Type[BaseModel]] = None,
                 search_response_model: Optional[Type[BaseModel]] = None,
                 crud: Optional[Type[AdminOperation]] = None,
                 unique_keys: Optional[List[str]] = None,
                 allowed_columns: Optional[List[str]] = None,
                 include_routes: Optional[Dict[str, bool]] = None,
                 ):
        self.crud = crud or AdminOperation
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
            crud=self.crud,
            unique_keys=unique_keys,
            allowed_columns=allowed_columns,
            include_routes=include_routes
        )

    def setup_custom_routes(self):
        super().setup_custom_routes()

        @self.router.get("/admin", response_model=ResponseAdmin)
        async def read_admin_data(current_user: ResponseAdmin = Depends(get_admin_user)):
            return current_user

    def _default_create_route(self):
        @self.router.post("/create_item/", response_model=self.response_model)
        async def create(
                name: Optional[str] = Form(default="无名者"),
                account: Optional[str] = Form(...),
                email: Optional[str] = Form(None),
                phone: Optional[str] = Form(None),
                status: Optional[bool] = Form(default=True),
                partition_id: Optional[int] = Form(None),
                hashed_password: Optional[str] = Form(...),
                db: AsyncSession = Depends(get_db)
        ):
            if not any([name, account, email, phone, status, partition_id, hashed_password]):
                raise HTTPException(status_code=400, detail="至少填写一个字段")

            model = self.create_model(
                name=name,
                account=account,
                email=email,
                phone=phone,
                status=status,
                partition_id=partition_id,
                hashed_password=hashed_password
            )
            return await self.crud.create_item(db=db, dbmodel=self.dbmodel, model=model,
                                               unique_keys=self.unique_keys)


def _default_update_route(self):
    @self.router.put("/update_item/", response_model=self.response_model)
    async def update(
            id: int = Form(...),
            name: Optional[str] = Form(None),
            account: Optional[str] = Form(None),
            email: Optional[str] = Form(None),
            phone: Optional[str] = Form(None),
            status: Optional[bool] = Form(None),
            partition_id: Optional[int] = Form(None),
            hashed_password: Optional[str] = Form(None),
            db: AsyncSession = Depends(get_db)
    ):
        if not any([name, account, email, phone, status, partition_id, hashed_password]):
            raise HTTPException(status_code=400, detail="must fill at least one field")

        model = self.update_model(
            id=id,
            name=name,
            account=account,
            email=email,
            phone=phone,
            status=status,
            partition_id=partition_id,
            hashed_password=hashed_password
        )
        return await self.crud.update_item(db=db, dbmodel=self.dbmodel, model=model,
                                           unique_keys=self.unique_keys)
