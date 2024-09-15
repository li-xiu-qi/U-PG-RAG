import asyncio
import time
import logging
from openai import RateLimitError
from app.serves.model_serves.llms.llm_types import LLMInput, LLMOutput

logger = logging.getLogger(__name__)


def rate_limited_call(retry_times: int = 6):
    def decorator(func):
        async def wrapper(self, task_input: LLMInput) -> LLMOutput:
            for count in range(retry_times):
                try:
                    if not await self.limitator.check_limit():
                        logger.debug("Rate limit exceeded, waiting for 10 seconds.")
                        await asyncio.sleep(10)

                    result = await func(self, task_input)

                    if hasattr(result, 'total_tokens'):
                        self.limitator.update_limit_status(tokens=result.total_tokens)
                    else:
                        raise ValueError("ModelOutput must have 'total_tokens' attribute")

                    return result
                except RateLimitError as e:
                    logger.warning(f"RateLimitError encountered: {e}, retry {count + 1}/{retry_times}.")
                    if count == retry_times - 1:
                        logger.error("Exceeded maximum retry attempts.")
                        raise e
                    await asyncio.sleep(10)
                    continue
            raise RuntimeError("Exceeded maximum retry attempts")

        return wrapper

    return decorator


class RateLimiter:
    def __init__(self, max_requests_per_minute, max_total_tokens_per_minute):
        self.max_requests_per_minute = max_requests_per_minute
        self.max_total_tokens_per_minute = max_total_tokens_per_minute
        self.current_request_count = 0
        self.current_total_tokens = 0
        self.start_time = self._get_int_time()
        self.status = True

    def _get_int_time(self):
        return int(time.time())

    async def check_limit(self):
        current_time = self._get_int_time()
        elapsed_time = current_time - self.start_time

        if elapsed_time >= 60:
            logger.debug("Resetting rate limiter after 60 seconds.")
            self.start_time = current_time
            self.current_request_count = 0
            self.current_total_tokens = 0
            self.status = True

        if self.current_request_count >= self.max_requests_per_minute or self.current_total_tokens >= self.max_total_tokens_per_minute:
            logger.warning("Rate limit reached: Pausing requests.")
            self.status = False
            return False

        self.status = True
        return True

    def update_limit_status(self, tokens=0):
        self.current_request_count += 1
        self.current_total_tokens += tokens
        logger.debug(
            f"Updated rate limiter status: {self.current_request_count} requests, {self.current_total_tokens} tokens.")
