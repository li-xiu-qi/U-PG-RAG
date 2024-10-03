from pydantic import BaseModel


class DataPrecess(BaseModel):
    partition_id: int
    chunk_size: int = 832
    chunk_overlap: int = 32
