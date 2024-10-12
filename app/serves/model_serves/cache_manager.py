import asyncio
import json
import logging
from functools import wraps

from app.core.create_cache_key import create_hash_key, acreate_hash_key
from app.serves.model_serves.types import LLMOutput, EmbeddingOutput

logger = logging.getLogger(__name__)


# only used in the llm chat function
def llm_cached_call():
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if not self.enable_cache:
                return await func(self, *args, **kwargs)

            model_input = args[0] if args else kwargs.get('model_input')

            llm_input = model_input.model_dump()
            messages = llm_input.get("input_content")
            parameters = llm_input.get("set_param")

            cache_key = create_hash_key(self.cache.partition_name, messages, parameters)

            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.debug(f"Cache hit: {cache_key}")
                result = LLMOutput(output=json.dumps(cached_result), total_tokens=0)
                return result

            logger.debug(f"Cache miss: {cache_key}")
            result = await func(self, *args, **kwargs)

            self.cache.set(cache_key, result.output, expire_after_seconds=self.cache_expire_after_seconds)
            return result

        return wrapper

    return decorator


# only used in the embedding function
def embedding_cached_call():
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if not self.enable_cache:
                return await func(self, *args, **kwargs)

            model_input = args[0] if args else kwargs.get('model_input')
            embedding_input = model_input.model_dump()
            input_content = embedding_input.get("input_content")
            parameters = embedding_input.get("set_params")
            new_input_contents = []
            results = [None] * len(input_content)
            cache_miss_indices = []
            total_tokens = 0
            # 并行创建key并获取缓存
            cache_key_tasks = [acreate_hash_key("test_embedding", content, parameters) for content in input_content]
            cache_keys = await asyncio.gather(*cache_key_tasks)

            async def async_cache_get(cache, key):
                return cache.get(key)

            cache_results = await asyncio.gather(*[async_cache_get(self.cache, cache_key) for cache_key in cache_keys])

            for idx, (cache_key, cached_result) in enumerate(zip(cache_keys, cache_results)):
                if cached_result:
                    logger.debug(f"Cache hit: {cache_key}")
                    results[idx] = cached_result
                else:
                    logger.debug(f"Cache miss: {cache_key}")
                    new_input_contents.append(input_content[idx])
                    cache_miss_indices.append(idx)

            if new_input_contents:
                model_input.input_content = new_input_contents
                result = await func(self, *args, **kwargs)

                async def set_cache(idx, res):
                    cache_key = await acreate_hash_key("test_embedding", input_content[idx], parameters)
                    self.cache.set(cache_key, res)
                    results[idx] = res

                await asyncio.gather(*[set_cache(idx, res) for idx, res in zip(cache_miss_indices, result.output)])
                total_tokens = result.total_tokens

            return EmbeddingOutput(output=results, total_tokens=total_tokens)

        return wrapper

    return decorator
