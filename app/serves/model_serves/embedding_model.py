import logging
from typing import TypeVar

from openai import AsyncClient
from pydantic import BaseModel

from app.serves.model_serves.cache_manager import embedding_cached_call
from app.serves.model_serves.rag_model import RAGModel
from app.serves.model_serves.types import EmbeddingInput, EmbeddingOutput

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TInput = TypeVar('TInput', bound=BaseModel)
TOutput = TypeVar('TOutput', bound=BaseModel)


class EmbeddingModel(RAGModel):

    @embedding_cached_call()
    async def embedding(self, *, model_input: EmbeddingInput, max_retries: int = 3) -> EmbeddingOutput:
        logger.info("Embedding request for model: %s", model_input.name)

        async def embedding_func(client: AsyncClient, limiter, model_input):
            response = await client.embeddings.create(
                model=model_input.name,
                input=model_input.input_content,
                # **model_input.set_params if model_input.set_params else {}
            )
            total_tokens = response.usage.total_tokens
            limiter.update_limit_status(tokens=total_tokens)
            logger.debug("Embedding response received with total tokens: %d", total_tokens)

            output = [data.embedding for data in response.data]
            return EmbeddingOutput(output=output, total_tokens=total_tokens)

        return await self._execute_with_retries(embedding_func, model_input, max_retries=max_retries)