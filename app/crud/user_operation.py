from datetime import timedelta
from typing import Optional, List

from fastapi import Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token, authenticate_user
from app.crud.admin_operation import AdminOperation
from app.crud.filter_utils.filters import FilterHandler


class UserOperation:
    def __init__(self, filter_handler: FilterHandler):
        self.db_model = filter_handler.db_model
        self.unique_keys = self.db_model.get_unique_columns()
        self.admin_operation = AdminOperation(filter_handler)

    async def create_item(self, *, db: AsyncSession, model: BaseModel):
        return await self.admin_operation.create_item(db=db, model=model)

    async def update_item(self, *, db: AsyncSession, model: BaseModel):
        return await self.admin_operation.update_item(db=db, model=model)

    async def authenticate_user(self, *, db: AsyncSession, username: str, password: str):
        return await authenticate_user(db=db, dbmodel=self.dbmodel, username=username, password=password)

    async def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        return await create_access_token(data=data, expires_delta=expires_delta)

    async def get_current_user(self, request: Request, token: str, db: AsyncSession):
        return await self.get_current_user(request=request, token=token, db=db)
