from typing import List, Type, Optional

from pydantic import BaseModel

from app.crud.base_operation import BaseOperation
from app.crud.search_utils import vector_search, hybrid_search
from app.serves.model_serves.types import EmbeddingInput
from contant import get_rag_embedding


class VectorOperation:
    def __init__(self):
        self.normal_operation = BaseOperation()

    async def get_item(self, db, dbmodel, model):
        return await self.normal_operation.get_item(db=db, dbmodel=dbmodel,
                                                    model=model)

    async def get_items(self, db, dbmodel, model):
        return await self.normal_operation.get_items(db=db, dbmodel=dbmodel,
                                                     model=model)

    async def create_item(self, db, dbmodel, model,
                          unique_keys):
        await self.process_vector_field(model)
        return await self.normal_operation.create_item(db=db, dbmodel=dbmodel,
                                                       model=model,
                                                       unique_keys=unique_keys)

    async def update_item(self, db, dbmodel, model,
                          unique_keys):
        await self.process_vector_field(model)
        return await self.normal_operation.update_item(db=db, dbmodel=dbmodel,
                                                       model=model, unique_keys=unique_keys)

    async def delete_item(self, db, dbmodel, model):
        return await self.normal_operation.delete_item(db=db, dbmodel=dbmodel, model=model)

    async def search(self, db, dbmodel, model, allowed_columns):
        return await self.normal_operation.search(db=db, dbmodel=dbmodel,
                                                  model=model,
                                                  allowed_columns=allowed_columns)

    @staticmethod
    async def process_vector_field(model: BaseModel):
        if model.vector is None and model.query_or_chunk:
            model_input = EmbeddingInput(input_content=[model.query_or_chunk])
            rag_embedding = get_rag_embedding()
            embedding_output = await  rag_embedding.embedding(model_input=model_input)
            model.vector = embedding_output.output[0]

    async def update_model_vectors(self, model: BaseModel) -> BaseModel:
        if hasattr(model, 'vector') and model.vector is None and hasattr(model, 'query_or_chunk'):
            await self.process_vector_field(model)
        return model

    async def vector_search(self, *, db, dbmodel, model: BaseModel) -> List:
        await self.update_model_vectors(model)
        return await vector_search(db, dbmodel, model)

    async def hybrid_search(self, *, db, dbmodel, model: BaseModel,
                            allowed_columns: List[str]) -> List:
        await self.update_model_vectors(model)
        return await hybrid_search(db, dbmodel, model, allowed_columns)
