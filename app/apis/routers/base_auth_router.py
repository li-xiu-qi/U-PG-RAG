from datetime import datetime, timedelta
from typing import Type, List, Optional, Dict, Callable

from fastapi import APIRouter, Depends, Request, Form
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.apis.deps import get_db
from app.apis.routers.base_crud_router import BaseCRUDRouter
from app.core.auth import authenticate_user, create_access_token
from app.crud.user_operation import UserOperation
from app.db.db_models import User
from app.register.user_auth_config import decode_and_validate_token, get_credentials_exception
from app.schemes.models.user_models import ResponseToken, ResponseUser
from config import ServeConfig


class BaseAuthRouter(BaseCRUDRouter):
    def __init__(
            self,
            router: APIRouter,
            dbmodel: Type,
            response_model: Optional[Type[BaseModel]] = None,
            create_model: Optional[Type[BaseModel]] = None,
            update_model: Optional[Type[BaseModel]] = None,
            get_item: Optional[Callable[[], BaseModel]] = None,
            get_items: Optional[Callable[[], BaseModel]] = None,
            keyword_search_model: Optional[Type[BaseModel]] = None,
            search_response_model: Optional[Type[BaseModel]] = None,
            crud: Optional[Type[UserOperation]] = None,
            unique_keys: Optional[List[str]] = None,
            allowed_columns: Optional[List[str]] = None,
            include_routes: Optional[Dict[str, bool]] = None,
    ):
        super().__init__(
            router=router,
            dbmodel=dbmodel,
            crud=crud or UserOperation,
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
        super().setup_custom_routes()
        self._setup_login_route()
        self._setup_refresh_token_route()
        self._setup_get_user_route()

    def _setup_login_route(self):
        @self.router.post("/login", response_model=ResponseToken)
        async def login_for_access_token(
                request: Request,
                username: str = Form(...),
                password: str = Form(...),
                db: AsyncSession = Depends(get_db)
        ):
            user = await authenticate_user(db=db, dbmodel=self.dbmodel, username=username, password=password)
            access_token = await create_access_token(data={"sub": user.account, "ip": request.client.host})
            return ResponseToken(
                access_token=access_token,
                token_type="bearer",
                expires_at=datetime.now() + timedelta(minutes=ServeConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
            )

    def _setup_refresh_token_route(self):
        @self.router.post("/refresh-token", response_model=ResponseToken)
        async def refresh_access_token(
                request: Request,
                token: str = Depends(ServeConfig.oauth2_scheme),
                db: AsyncSession = Depends(get_db)
        ):
            payload = decode_and_validate_token(token, request.client.host)
            username = payload.get("sub")

            user = await db.execute(select(self.dbmodel).filter(self.dbmodel.account == username))
            user = user.scalar_one_or_none()
            if user is None:
                raise get_credentials_exception()

            access_token = await create_access_token(data={"sub": user.account, "ip": request.client.host})
            return ResponseToken(
                access_token=access_token,
                token_type="bearer",
                expires_at=datetime.now() + timedelta(minutes=ServeConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
            )

    def _setup_get_user_route(self):
        @self.router.get("/users/get_user", response_model=ResponseUser)
        async def get_current_user(request: Request, token: str = Depends(ServeConfig.oauth2_scheme),
                                   db: AsyncSession = Depends(get_db)) -> ResponseUser:
            payload = decode_and_validate_token(token, request.client.host)
            username = payload.get("sub")

            user = await db.execute(select(User).filter(User.account == username))
            user = user.scalar_one_or_none()
            if user is None:
                raise get_credentials_exception()

            return user
