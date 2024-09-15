from datetime import timedelta
from typing import Type, Optional, List

from fastapi import Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token, authenticate_user
from app.crud.admin_operation import AdminOperation


class UserOperation:
    def __init__(self):
        self.super_admin_operation = AdminOperation()

    async def create_item(self, *, db: AsyncSession,
                          dbmodel: Type,
                          model: BaseModel,
                          unique_keys: Optional[List[str]] = None,
                          ):
        return await self.super_admin_operation.create_item(db=db,
                                                            dbmodel=dbmodel,
                                                            model=model,
                                                            unique_keys=unique_keys)

    async def update_item(self,
                          *,
                          db: AsyncSession,
                          dbmodel: Type,
                          model: BaseModel,
                          unique_keys: Optional[List[str]] = None,
                          ):
        return await self.super_admin_operation.update_item(db=db,
                                                            dbmodel=dbmodel,
                                                            model=model,
                                                            unique_keys=unique_keys)

    async def authenticate_user(self, *, db: AsyncSession, dbmodel: Type, username: str, password: str):
        return await authenticate_user(db=db,
                                       dbmodel=dbmodel,
                                       username=username,
                                       password=password)

    async def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        return await create_access_token(data=data, expires_delta=expires_delta)

    async def get_current_user(self, request: Request, token: str, db: AsyncSession, dbmodel: Type):
        return await self.get_current_user(request=request, token=token, db=db, dbmodel=dbmodel)
