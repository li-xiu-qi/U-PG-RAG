import asyncio
from typing import TypeVar, AsyncGenerator, Callable, Any

from openai import RateLimitError, APIConnectionError, APITimeoutError
from pg_cache import AsyncPgCache
from pydantic import BaseModel

from app.serves.model_serves.cache_manager import cached_call, logger
from app.serves.model_serves.client_manager import ClientManager
from app.serves.model_serves.types import LLMInput, LLMOutput, EmbeddingOutput, EmbeddingInput
from config import ServeConfig

TInput = TypeVar('TInput', bound=BaseModel)
TOutput = TypeVar('TOutput', bound=BaseModel)


class RAG:

    def __init__(self, client_manager: ClientManager,
                 buffer: AsyncPgCache = None,
                 cache_expire_after_seconds: int | None = None):
        self.client_manager = client_manager
        self.cache_expire_after_seconds = cache_expire_after_seconds
        self.enable_cache = buffer is not None
        self.buffer = buffer

    def _obfuscate_api_key(self, api_key: str) -> str:
        """Obfuscate the API key to avoid exposing it directly."""
        return api_key[:4] + '****' + api_key[-4:]

    async def _execute_with_retries(self, func: Callable[..., Any], *args, max_retries: int = 3, **kwargs) -> Any:
        async with self.client_manager.semaphore:
            retry_count = 0

            while retry_count < max_retries * len(self.client_manager.api_configs):
                client, limiter = await self.client_manager.get_client()

                try:
                    result = func(client, limiter, *args, **kwargs)
                    if hasattr(result, '__aiter__'):
                        return self._handle_async_generator(result)
                    else:
                        return await result

                except (RateLimitError, APIConnectionError, APITimeoutError) as e:
                    obfuscated_key = self._obfuscate_api_key(limiter.api_key)
                    logger.warning(f"Error {e.__class__.__name__} with API key {obfuscated_key}, retrying...")

                    retry_count += 1
                    wait_time = min(60, 2 ** retry_count)
                    logger.info(f"Waiting for {wait_time} seconds before retrying.")
                    await asyncio.sleep(wait_time)

                    if isinstance(e, RateLimitError):
                        limiter.block(50)

                    self.client_manager.rotate_client()

            await asyncio.sleep(60)
            return await self._execute_with_retries(func, *args, max_retries=max_retries, **kwargs)

    async def _handle_async_generator(self, async_gen):
        async for item in async_gen:
            yield item

    @cached_call()
    async def chat(self, model_input: LLMInput, max_retries: int = 3) -> LLMOutput:
        async def chat_func(client, limiter, model_input):
            response = await client.chat.completions.create(
                model=model_input.name,
                messages=model_input.input_content,
                **model_input.set_param or {},
            )
            total_tokens = response.usage.total_tokens
            limiter.update_limit_status(tokens=total_tokens)

            return LLMOutput(output=response.choices[0].message.content, total_tokens=total_tokens)

        return await self._execute_with_retries(chat_func, model_input, max_retries=max_retries)

    async def stream_chat(self, model_input: LLMInput, max_retries: int = 3) -> AsyncGenerator[LLMOutput, None]:
        async def stream_chat_func(client, limiter, model_input):
            response = await client.chat.completions.create(
                model=model_input.name,
                messages=model_input.input_content,
                **model_input.set_param or {},
                stream=True
            )
            async for chunk in response:
                if chunk.choices[0].finish_reason:
                    total_tokens = chunk.usage.total_tokens
                    limiter.update_limit_status(tokens=total_tokens)
                    yield LLMOutput(output="", total_tokens=total_tokens)
                else:
                    output = chunk.choices[0].delta.content or ""
                    yield LLMOutput(output=output, total_tokens=0)

        async for item in await self._execute_with_retries(stream_chat_func, model_input, max_retries=max_retries):
            yield item

    @cached_call()
    async def embedding(self, model_input: EmbeddingInput, max_retries: int = 3) -> EmbeddingOutput:
        async def embedding_func(client, limiter, model_input):
            response = await client.embeddings.create(
                model=model_input.name,
                input=model_input.input_content,
                **model_input.set_params if model_input.set_params else {}
            )
            total_tokens = response.usage.total_tokens
            limiter.update_limit_status(tokens=total_tokens)

            output = [data.embedding for data in response.data]
            return EmbeddingOutput(output=output, total_tokens=total_tokens)

        return await self._execute_with_retries(embedding_func, model_input, max_retries=max_retries)


