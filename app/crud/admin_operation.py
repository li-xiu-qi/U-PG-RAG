from typing import List, Optional, Type

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base_operation import BaseOperation
from config import ServeConfig


class AdminOperation:
    def __init__(self):
        self.normal_operation = BaseOperation()

    async def create_item(self, *, db: AsyncSession,
                          dbmodel: Type,
                          model: BaseModel,
                          unique_keys: Optional[List[str]] = None):
        model_dict = model.model_dump(exclude_unset=True)
        model_dict['role'] = model_dict.get('role', 'user')

        if 'hashed_password' in model_dict:
            model_dict['hashed_password'] = ServeConfig.pwd_context.hash(model_dict['hashed_password'])

        updated_model = model.__class__(**model_dict)

        return await self.normal_operation.create_item(db=db, dbmodel=dbmodel, model=updated_model,
                                                       unique_keys=unique_keys)

    async def update_item(self, *, db: AsyncSession, dbmodel: Type,
                          model: BaseModel,
                          unique_keys: Optional[List[str]] = None):
        model_dict = model.model_dump(exclude_unset=True)
        if 'hashed_password' in model_dict:
            model_dict['hashed_password'] = ServeConfig.pwd_context.hash(model_dict['hashed_password'])

        # 创建新的模型实例
        updated_model = model.__class__(**model_dict)

        return await self.normal_operation.update_item(db=db, dbmodel=dbmodel, model=updated_model,
                                                       unique_keys=unique_keys)

    async def get_item(self, *, db: AsyncSession, dbmodel: Type, model: BaseModel):
        return await self.normal_operation.get_item(db=db, dbmodel=dbmodel, model=model)

    async def get_items(self, *, db: AsyncSession, dbmodel: Type, model: BaseModel):
        return await self.normal_operation.get_items(db=db, dbmodel=dbmodel, model=model)

    async def delete_item(self, *, db: AsyncSession, dbmodel: Type, model: BaseModel):
        return await self.normal_operation.delete_item(db=db, dbmodel=dbmodel, model=model)

    async def search(self, *, db: AsyncSession, dbmodel: Type, model: BaseModel):
        return await self.normal_operation.search(db=db, dbmodel=dbmodel, model=model)
