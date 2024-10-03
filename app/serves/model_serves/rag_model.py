import asyncio
import logging
from typing import TypeVar, Callable, Any

from diskcache import Cache
from openai import RateLimitError, APIConnectionError, APITimeoutError
from pg_cache import PgCache
from pydantic import BaseModel

from app.serves.model_serves.client_manager import ClientManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TInput = TypeVar('TInput', bound=BaseModel)
TOutput = TypeVar('TOutput', bound=BaseModel)


class RAGModel:

    def __init__(self, client_manager: ClientManager,
                 cache: PgCache | Cache = None,
                 cache_expire_after_seconds: int | None = None):
        self.client_manager = client_manager
        self.cache_expire_after_seconds = cache_expire_after_seconds
        self.enable_cache = cache is not None
        self.cache = cache
        logger.info("initialized with cache: %s", self.enable_cache)

    def _obfuscate_api_key(self, api_key: str) -> str:
        """Obfuscate the API key to avoid exposing it directly."""
        return api_key[:4] + '****' + api_key[-4:]

    async def _execute_with_retries(self, func: Callable[..., Any], *args, max_retries: int = 3, **kwargs) -> Any:
        async with self.client_manager.semaphore:
            retry_count = 0
            logger.info("Starting execution with retries, max_retries: %d", max_retries)

            while retry_count < max_retries * len(self.client_manager.api_configs):
                client, limiter = await self.client_manager.get_client()
                logger.debug("Using client with API key: %s", self._obfuscate_api_key(limiter.api_key))

                try:
                    result = func(client, limiter, *args, **kwargs)
                    if hasattr(result, '__aiter__'):
                        return self._handle_async_generator(result)
                    else:
                        return await result

                except (RateLimitError, APIConnectionError, APITimeoutError) as e:
                    obfuscated_key = self._obfuscate_api_key(limiter.api_key)
                    logger.warning("Error %s with API key %s, retrying...", e.__class__.__name__, obfuscated_key)

                    retry_count += 1
                    wait_time = min(60, 2 ** retry_count)
                    logger.info("Waiting for %d seconds before retrying.", wait_time)
                    await asyncio.sleep(wait_time)

                    if isinstance(e, RateLimitError):
                        limiter.block(50)

                    self.client_manager.rotate_client()

            logger.error("Max retries reached, retrying after 60 seconds.")
            await asyncio.sleep(60)
            return await self._execute_with_retries(func, *args, max_retries=max_retries, **kwargs)

    async def _handle_async_generator(self, async_gen):
        async for item in async_gen:
            yield item
