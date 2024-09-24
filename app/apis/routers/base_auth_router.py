from typing import Type, Optional, Dict

from fastapi import APIRouter, Depends, Request, Form
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.apis.deps import get_db
from app.apis.routers.base_crud_router import BaseCRUDRouter
from app.core.auth import authenticate_user, create_access_token, get_credentials_exception, decode_and_validate_token
from app.crud.admin_operation import AdminOperation
from app.crud.user_operation import UserOperation
from app.db.db_models import User
from app.schemes.models.user_models import ResponseToken, ResponseUser
from config import ServeConfig


class BaseAuthRouter(BaseCRUDRouter):
    operator: UserOperation | AdminOperation

    def __init__(
            self,
            router: APIRouter,
            operator: UserOperation,
            response_model: Optional[Type[BaseModel]] = None,
            create_model: Optional[Type[BaseModel]] = None,
            update_model: Optional[Type[BaseModel]] = None,
            keyword_search_model: Optional[Type[BaseModel]] = None,
            search_response_model: Optional[Type[BaseModel]] = None,
            include_routes: Optional[Dict[str, bool]] = None,
    ):
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
            user = await authenticate_user(db=db, dbmodel=User, username=username, password=password)
            access_token, expires_at = await create_access_token(
                data={"sub": user.account, "ip": request.client.host, "scope": "user"}
            )
            return ResponseToken(
                access_token=access_token,
                token_type="bearer",
                expires_at=expires_at
            )

    def _setup_refresh_token_route(self):
        @self.router.post("/refresh-token", response_model=ResponseToken)
        async def refresh_access_token(
                request: Request,
                token: str = Depends(ServeConfig.oauth2_scheme),
                db: AsyncSession = Depends(get_db)
        ):
            user = await self._get_user_from_token(token, request.client.host, db)
            access_token, expires_at = await create_access_token(
                data={"sub": user.account, "ip": request.client.host, "scope": "user"}
            )
            return ResponseToken(
                access_token=access_token,
                token_type="bearer",
                expires_at=expires_at
            )

    def _setup_get_user_route(self):
        @self.router.get("/users/get_user", response_model=ResponseUser)
        async def get_current_user(request: Request, token: str = Depends(ServeConfig.oauth2_scheme),
                                   db: AsyncSession = Depends(get_db)):
            user = await self._get_user_from_token(token, request.client.host, db)
            return user

    async def _get_user_from_token(self, token: str, client_ip: str, db: AsyncSession):
        payload = decode_and_validate_token(token, client_ip, required_scope="user")
        user_account = payload.get("sub")

        user = await db.execute(select(User).filter(User.account == user_account))
        user = user.scalar_one_or_none()
        if user is None:
            raise get_credentials_exception()

        return user
