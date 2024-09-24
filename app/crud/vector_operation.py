from typing import List
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base_operation import BaseOperation
from app.crud.search_utils import vector_search, hybrid_search
from app.serves.model_serves.types import EmbeddingInput
from contant import get_rag_embedding
from app.crud.filter_utils.filters import FilterHandler


class VectorOperation(BaseOperation):
    def __init__(self, filter_handler: FilterHandler):
        super().__init__(filter_handler)
        self.unique_keys = self.db_model.get_unique_columns()

    @staticmethod
    async def process_vector_field(model: BaseModel):
        if model.vector is None and model.query_or_chunk:
            model_input = EmbeddingInput(input_content=[model.query_or_chunk])
            rag_embedding = get_rag_embedding()
            embedding_output = await rag_embedding.embedding(model_input=model_input)
            model.vector = embedding_output.output[0]

    async def update_model_vectors(self, model: BaseModel) -> BaseModel:
        if hasattr(model, 'vector') and model.vector is None and hasattr(model, 'query_or_chunk'):
            await self.process_vector_field(model)
        return model

    async def vector_search(self, *, db: AsyncSession, model: BaseModel) -> List:
        await self.update_model_vectors(model)
        return await vector_search(db, model, self.filter_handler)

    async def hybrid_search(self, *, db: AsyncSession, model: BaseModel) -> List:
        await self.update_model_vectors(model)
        return await hybrid_search(db, model, self.filter_handler)
