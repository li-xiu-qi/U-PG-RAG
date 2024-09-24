from typing import List

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.filter_utils.filters import FilterHandler
from app.crud.search_utils import search


class BaseOperation:
    def __init__(self, filter_handler: FilterHandler):
        self.filter_handler = filter_handler
        self.db_model = filter_handler.db_model

    async def get_item(self, *, db: AsyncSession, _id: int):
        query = select(self.db_model).where(self.db_model.id == _id)
        result = await db.execute(query)
        item = result.scalar_one_or_none()
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return item

    async def get_items(self, *, db: AsyncSession, offset: int = 0, limit: int = 20):
        query = select(self.db_model).offset(offset).limit(limit)
        result = await db.execute(query)
        items = result.scalars().all()
        return items

    async def read_item(self, *, db: AsyncSession, model: BaseModel):
        model_dict = model.model_dump(exclude_unset=True)
        _id = model_dict.pop("id", None)
        filters = model_dict.pop("filters", {})
        ###
        if filters:
            filters = filters.pop("filters", {})
        ###
        query = select(self.db_model)

        if filters:
            filter_clause = self.filter_handler.create_filter_clause(filters)
            query = query.where(filter_clause)

        if _id:
            query = query.where(self.db_model.id == _id)
            result = await db.execute(query)
            item = result.scalar_one_or_none()
            if item is None:
                raise HTTPException(status_code=404, detail="Item not found")
            return item
        else:
            raise HTTPException(status_code=400, detail="ID is required for getting an item.")

    async def read_items(self, *, db: AsyncSession, model: BaseModel) -> List:
        model_dict = model.model_dump(exclude_unset=True)
        filters = model_dict.pop("filters", {})

        offset = model_dict.pop("offset", 0)
        limit = model_dict.pop("limit", 20)
        query = select(self.db_model)

        if filters:
            filter_clause = self.filter_handler.create_filter_clause(filters)
            query = query.where(filter_clause)

        query = query.offset(offset).limit(limit)
        result = await db.execute(query)
        results = result.scalars().all()
        return results

    async def create_item(self, *, db: AsyncSession, model: BaseModel,
                          ):
        model_dict = model.model_dump(exclude_unset=True)
        self.unique_keys = self.db_model.get_unique_columns()
        if self.unique_keys:
            conflict_filters = {key: model_dict[key] for key in self.unique_keys if key in model_dict}
            query = select(self.db_model).filter_by(**conflict_filters)
            result = await db.execute(query)
            existing_item = result.scalar_one_or_none()

            if existing_item:
                raise HTTPException(status_code=409,
                                    detail=f"Conflict detected: The item with {conflict_filters} already exists.")

        db_item = self.db_model(**model_dict)
        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)
        return db_item

    async def update_item(self, *, db: AsyncSession, model: BaseModel):
        model_dict = model.model_dump(exclude_unset=True)
        model_id = model_dict.pop("id", None)
        self.unique_keys = self.db_model.get_unique_columns()
        conflict_filters = {}
        if self.unique_keys:
            conflict_filters = {key: model_dict[key] for key in self.unique_keys if key in model_dict}

        if not model_id:
            raise HTTPException(status_code=400, detail="ID is required for updating an item.")

        query = select(self.db_model).where(self.db_model.id == model_id)
        result = await db.execute(query)
        existing_item = result.scalar_one_or_none()

        if not existing_item:
            raise HTTPException(status_code=404, detail=f"Item with ID {model_id} does not exist.")

        if conflict_filters:
            conflict_query = select(self.db_model).filter_by(**conflict_filters).where(self.db_model.id != model_id)
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

    async def delete_item(self, *, db: AsyncSession, _id: int):
        if not _id:
            raise HTTPException(status_code=400, detail="ID is required for deleting an item.")

        query = select(self.db_model).where(self.db_model.id == _id)
        result = await db.execute(query)
        existing_item = result.scalar_one_or_none()

        if not existing_item:
            raise HTTPException(status_code=404, detail=f"Item with ID {_id} does not exist.")

        exclude_relationships = self.db_model.get_relationship()
        for relationship_name in exclude_relationships:
            relationship_items = await db.run_sync(lambda _: getattr(existing_item, relationship_name))
            for item in relationship_items:
                for fk in item.__table__.foreign_keys:
                    if fk.column.table == self.db_model.__table__:
                        setattr(item, fk.parent.name, None)
                db.add(item)
            await db.commit()

        await db.delete(existing_item)
        await db.commit()
        return existing_item

    async def search(self, *, db: AsyncSession, model: BaseModel) -> List:
        return await search(db=db, model=model, filter_handler=self.filter_handler)
