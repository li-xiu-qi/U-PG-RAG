from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload
from fastapi import HTTPException
from app.schemes.model_filters import PartitionFilter
from app.db.db_models import File


class FileCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_file(self, file_data: dict) -> dict:
        new_file = File(**file_data)
        self.db.add(new_file)
        await self.db.commit()
        await self.db.refresh(new_file)
        return new_file.__dict__

    async def get_file(self, file_id: int, partition_filter: Optional[PartitionFilter] = None) -> dict:
        query = select(File).options(joinedload(File.partition)).filter(File.id == file_id)

        # 如果提供了分区过滤器，则进行分区过滤
        if partition_filter and partition_filter.partition_id is not None:
            query = query.filter(File.partition_id == partition_filter.partition_id)

        result = await self.db.execute(query)
        file = result.scalar_one_or_none()
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        return file.__dict__

    async def get_file_by_hash(self, file_hash: str, partition_filter: Optional[PartitionFilter] = None) -> Optional[
        File]:
        query = select(File).filter(File.file_hash == file_hash)

        # 分区过滤
        if partition_filter and partition_filter.partition_id is not None:
            query = query.filter(File.partition_id == partition_filter.partition_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_file(self, file: File, updates: dict) -> dict:
        try:
            for key, value in updates.items():
                setattr(file, key, value)
            await self.db.commit()
            await self.db.refresh(file)
            return file.__dict__
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_file(self, file_id: int, partition_filter: Optional[PartitionFilter] = None) -> None:
        query = select(File).filter(File.id == file_id)

        # 分区过滤
        if partition_filter and partition_filter.partition_id is not None:
            query = query.filter(File.partition_id == partition_filter.partition_id)

        result = await self.db.execute(query)
        file = result.scalar_one_or_none()
        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        if file.reference_count > 1:
            file.reference_count -= 1
            await self.db.commit()
        else:
            await self.db.delete(file)
            await self.db.commit()

    async def get_multiple_files(
            self,
            partition_filter: Optional[PartitionFilter] = None,
            offset: int = 0,
            limit: int = 20
    ) -> List[File]:
        query = select(File)

        # 应用分区过滤器
        if partition_filter and partition_filter.partition_id is not None:
            query = query.filter(File.partition_id == partition_filter.partition_id)

        # 应用分页
        query = query.offset(offset).limit(limit)

        result = await self.db.execute(query)
        files = result.scalars().all()

        if not files:
            raise HTTPException(status_code=404, detail="No files found")

        return files