import asyncio
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

    async def embed_query(self, model_input: EmbeddingInput, max_retries: int = 3):
        embedding_output = await self.embedding(model_input=model_input, max_retries=max_retries)
        return embedding_output

    async def embed_func(self, model_input: EmbeddingInput, max_retries: int = 3):
        # 分批次每一批次的大小不能超过64,内的列表字符串长度总和不能超过50000
        result = EmbeddingOutput(output=[], total_tokens=0)
        batches = []
        batch = []
        batch_length = 0

        for content in model_input.input_content:
            content_length = len(content)
            if len(batch) < 64 and (batch_length + content_length) <= 50000:
                batch.append(content)
                batch_length += content_length
            else:
                batches.append(batch)
                batch = [content]
                batch_length = content_length

        if batch:
            batches.append(batch)

        async def process_batch(batch):
            batch_input = EmbeddingInput(name=model_input.name, input_content=batch)
            return await self.embedding(model_input=batch_input, max_retries=max_retries)

        embedding_outputs = await asyncio.gather(*[process_batch(batch) for batch in batches])

        for embedding_output in embedding_outputs:
            result.output.extend(embedding_output.output)
            result.total_tokens += embedding_output.total_tokens

        return result
