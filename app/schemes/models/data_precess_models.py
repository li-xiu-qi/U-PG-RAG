from pydantic import BaseModel


class DataPrecess(BaseModel):
    partition_id: int
