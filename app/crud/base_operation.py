import copy
from typing import List, Optional, Type

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.search_utils import search


class BaseOperation:
    async def get_item(self, *, db: AsyncSession, dbmodel: Type, model: BaseModel):
        model_dict = model.model_dump(exclude_unset=True)
        model_id = model_dict.pop("id", None)
        filters = model_dict.pop("filters", {})

        query = select(dbmodel)

        if filters:
            query = query.filter_by(**filters)

        if model_id:
            query = query.where(dbmodel.id == model_id)
            result = await db.execute(query)
            item = result.scalar_one_or_none()
            if item is None:
                raise HTTPException(status_code=404, detail="Item not found")
            return item
        else:
            raise ValueError("ID is required for getting an item.")

    async def get_items(self, *, db: AsyncSession, dbmodel: Type, model: BaseModel) -> List:
        model_dict = model.model_dump(exclude_unset=True)
        filters = model_dict.pop("filters", {})

        offset = model_dict.pop("offset", 0)
        limit = model_dict.pop("limit", 20)
        query = select(dbmodel)

        if filters:
            query = query.filter_by(**filters)

        query = query.offset(offset).limit(limit)
        result = await db.execute(query)
        results = result.scalars().all()
        return results

    async def create_item(self, *, db: AsyncSession, dbmodel: Type, model: BaseModel,
                          unique_keys: Optional[List[str]] = None):
        model_dict = model.model_dump(exclude_unset=True)

        if unique_keys:
            conflict_filters = {key: model_dict[key] for key in unique_keys if key in model_dict}
            query = select(dbmodel).filter_by(**conflict_filters)
            result = await db.execute(query)
            existing_item = result.scalar_one_or_none()

            if existing_item:
                raise HTTPException(status_code=409,
                                    detail=f"Conflict detected: The item with {conflict_filters} already exists.")

        db_item = dbmodel(**model_dict)
        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)
        return db_item

    @staticmethod
    async def update_item(*, db: AsyncSession, dbmodel: Type, model: BaseModel,
                          unique_keys: Optional[List[str]] = None):
        model_dict = model.model_dump(exclude_unset=True)
        model_id = model_dict.pop("id", None)
        conflict_filters = {key: model_dict[key] for key in unique_keys if key in model_dict}

        if not model_id:
            raise HTTPException(status_code=400, detail="ID is required for updating an item.")

        query = select(dbmodel).where(dbmodel.id == model_id)
        result = await db.execute(query)
        existing_item = result.scalar_one_or_none()

        if not existing_item:
            raise HTTPException(status_code=404, detail=f"Item with ID {model_id} does not exist.")

        if conflict_filters:
            conflict_query = select(dbmodel).filter_by(**conflict_filters).where(dbmodel.id != model_id)
            conflict_result = await db.execute(conflict_query)
            conflicting_item = conflict_result.scalar_one_or_none()

            if conflicting_item:
                raise HTTPException(status_code=409,
                                    detail=f"Conflict detected: The item with {conflict_filters} already exists.")

        for key, value in model_dict.items():
            setattr(existing_item, key, value)

        db.add(existing_item)
        await db.commit()
        await db.refresh(existing_item)
        return existing_item

    async def delete_item(self, *, db: AsyncSession, dbmodel: Type, model: BaseModel):
        model_dict = model.model_dump(exclude_unset=True)
        model_id = model_dict.pop("id", None)

        if not model_id:
            raise ValueError("ID is required for deleting an item.")

        query = select(dbmodel).where(dbmodel.id == model_id)
        result = await db.execute(query)
        existing_item = result.scalar_one_or_none()

        if not existing_item:
            raise ValueError(f"Item with ID {model_id} does not exist.")

        await db.delete(existing_item)
        await db.commit()
        return existing_item

    async def search(self, *, db: AsyncSession, dbmodel: Type, model: BaseModel,
                     allowed_columns: Optional[List[str]] = None) -> List:
        return await search(db, dbmodel=dbmodel, model=model, allowed_columns=allowed_columns)
