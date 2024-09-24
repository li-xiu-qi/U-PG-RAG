from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base_operation import BaseOperation
from config import ServeConfig
from app.crud.filter_utils.filters import FilterHandler


class AdminOperation(BaseOperation):
    def __init__(self, filter_handler: FilterHandler):
        super().__init__(filter_handler)
        self.unique_keys = self.db_model.get_unique_columns()


    async def create_item(self, *, db: AsyncSession, model: BaseModel):
        model_dict = model.model_dump(exclude_unset=True)
        model_dict['role'] = model_dict.get('role', 'user')

        if 'hashed_password' in model_dict:
            model_dict['hashed_password'] = ServeConfig.pwd_context.hash(model_dict['hashed_password'])

        updated_model = model.__class__(**model_dict)

        return await super().create_item(db=db, model=updated_model)

    async def update_item(self, *, db: AsyncSession, model: BaseModel):
        model_dict = model.model_dump(exclude_unset=True)
        if 'hashed_password' in model_dict:
            model_dict['hashed_password'] = ServeConfig.pwd_context.hash(model_dict['hashed_password'])

        updated_model = model.__class__(**model_dict)

        return await super().update_item(db=db, model=updated_model)