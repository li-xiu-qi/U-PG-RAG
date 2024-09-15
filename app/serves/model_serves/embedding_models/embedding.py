from app.serves.model_serves.base_models import AsyncBaseModel
from app.serves.model_serves.embedding_models.embedding_types import EmbeddingInput, EmbeddingOutput


class AsyncEmbedding(AsyncBaseModel[EmbeddingInput, EmbeddingOutput]):
    async def __call__(self, model_input: EmbeddingInput) -> EmbeddingOutput:
        response = await self.get_client().embeddings.create(
            model=model_input.model_name,
            input=model_input.input_content,
            **model_input.model_parameters if model_input.model_parameters else {},
        )
        output = [data.embedding for data in response.data]
        total_tokens = response.usage.prompt_tokens
        return EmbeddingOutput(task_output=output, total_tokens=total_tokens)
