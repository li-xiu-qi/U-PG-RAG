import time
import logging
from typing import Union

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self, api_key: str, max_rpm: Union[int, None] = None, max_tpm: Union[int, None] = None):
        self.api_key = api_key
        self.max_requests_per_minute = max_rpm
        self.max_total_tokens_per_minute = max_tpm
        self.current_request_count = 0
        self.current_total_tokens = 0
        self.start_time = self._get_int_time()
        self.is_blocked = False
        self.blocked_until = None

    def _get_int_time(self):
        return int(time.time())

    async def check_limit(self):
        if self.is_blocked:
            if time.time() < self.blocked_until:
                logger.info(f"API key {self._obfuscate_api_key()} is temporarily blocked until {self.blocked_until}.")
                return False
            else:
                self.is_blocked = False

        current_time = self._get_int_time()
        elapsed_time = current_time - self.start_time

        if elapsed_time >= 60:
            logger.debug("Resetting rate limiter after 60 seconds.")
            self.start_time = current_time
            self.current_request_count = 0
            self.current_total_tokens = 0

        if (self.max_requests_per_minute is not None and self.current_request_count >= self.max_requests_per_minute) or \
                (
                        self.max_total_tokens_per_minute is not None and self.current_total_tokens >= self.max_total_tokens_per_minute):
            logger.warning(f"Rate limit reached for API key {self._obfuscate_api_key()}.")
            return False

        return True

    def update_limit_status(self, tokens: int = 0):
        self.current_request_count += 1
        self.current_total_tokens += tokens
        logger.debug(
            f"API key {self._obfuscate_api_key()}: {self.current_request_count} requests, {self.current_total_tokens} tokens.")

    def block(self, duration: int):
        """Temporarily block the API for a given duration in seconds."""
        self.is_blocked = True
        self.blocked_until = time.time() + duration
        logger.warning(f"Blocking API key {self._obfuscate_api_key()} for {duration} seconds.")

    def _obfuscate_api_key(self):
        """Obfuscate the API key to avoid exposing it directly."""
        return self.api_key[:4] + '****' + self.api_key[-4:]
