from functools import wraps
import logging

from app.core.create_cache_key import create_hash_key

logger = logging.getLogger(__name__)


def cached_call():
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if not self.enable_cache:
                return await func(self, *args, **kwargs)

            messages = kwargs.get("messages", [])
            parameters = kwargs.get("parameters", {})

            cache_key = create_hash_key(self.task, messages, parameters)

            cached_result = await self.buffer.get(cache_key)
            if cached_result:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_result

            logger.debug(f"Cache miss: {cache_key}")
            result = await func(self, *args, **kwargs)

            await self.buffer.set(cache_key, result, expire_after_seconds=60)
            return result

        return wrapper

    return decorator
