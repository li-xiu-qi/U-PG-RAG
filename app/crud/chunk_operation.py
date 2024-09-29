from typing import List
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base_operation import BaseOperation
from app.crud.search_utils import vector_search, hybrid_search
from app.serves.model_serves.types import EmbeddingInput
from contant import get_rag_embedding
from app.crud.filter_utils.filters import FilterHandler


class ChunkOperation(BaseOperation):
    def __init__(self, filter_handler: FilterHandler):
        super().__init__(filter_handler)
        self.unique_keys = self.db_model.get_unique_columns()

    @staticmethod
    async def process_vector_field(model: BaseModel):
        if model.vector is None and model.page_content:
            model_input = EmbeddingInput(input_content=[model.page_content])
            rag_embedding = get_rag_embedding()
            embedding_output = await rag_embedding.embedding(model_input=model_input)
            model.vector = embedding_output.output[0]

    async def create_item(self, *, db: AsyncSession, model: BaseModel):
        await self.process_vector_field(model)
        return await super().create_item(db=db, model=model)

    async def filter_and_create_items(self, *, db: AsyncSession, models: List[BaseModel]):
        filtered_models = []
        seen_contents = set()
        page_contents = []

        # 过滤重复内容
        for model in models:
            if model.page_content and model.page_content not in seen_contents:
                filtered_models.append(model)
                seen_contents.add(model.page_content)
                page_contents.append(model.page_content)

        total_length = 0
        current_chunk = []
        current_chunk_models = []
        chunks = []
        chunked_models = []

        # 根据文本长度和批次大小拆分批次
        for model, content in zip(filtered_models, page_contents):
            content_length = len(content)
            if total_length + content_length > 50000 or len(current_chunk) >= 64:
                chunks.append(current_chunk)
                chunked_models.append(current_chunk_models)
                current_chunk = [content]
                current_chunk_models = [model]
                total_length = content_length
            else:
                current_chunk.append(content)
                current_chunk_models.append(model)
                total_length += content_length

        if current_chunk:
            chunks.append(current_chunk)
            chunked_models.append(current_chunk_models)

        rag_embedding = get_rag_embedding()

        # 处理每个批次
        for chunk, models_chunk in zip(chunks, chunked_models):
            model_input = EmbeddingInput(input_content=chunk)
            embedding_output = await rag_embedding.embedding(model_input=model_input)
            vectors = embedding_output.output

            # 更新模型向量
            for model, vector in zip(models_chunk, vectors):
                model.vector = vector

        await super().create_items(db=db, models=filtered_models)

    async def vector_search(self, *, db: AsyncSession, model: BaseModel) -> List:
        await self.process_vector_field(model)
        return await vector_search(db, model, self.filter_handler)

    async def hybrid_search(self, *, db: AsyncSession, model: BaseModel) -> List:
        await self.process_vector_field(model)
        return await hybrid_search(db, model, self.filter_handler)
