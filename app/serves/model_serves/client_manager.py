import asyncio
from typing import List, Dict, Union

from openai import AsyncOpenAI

from app.serves.model_serves.rate_limiter import RateLimiter
from config import ServeConfig


class ClientManager:
    def __init__(self, api_configs: List[Dict[str, Union[str, int, None]]],
                 cache_expire_after_seconds: int | None = None, max_concurrent_requests: int = 5):
        self.api_configs = api_configs

        if self.api_configs:
            self.limiters = [RateLimiter(config['api_key'], config.get('rpm'), config.get('tpm')) for config in
                             self.api_configs]
        elif ServeConfig.api_key:
            self.limiters = [RateLimiter(ServeConfig.api_key, None, None)]
        else:
            raise ValueError("api_configs must be a list of dictionaries with 'api_key' and 'base_url' keys")

        self.client_index = 0
        ###
        self.base_urls = [config['base_url'] for config in self.api_configs]
        self.base_url = self.base_urls[self.client_index]
        ###
        if self.api_configs:
            self.clients = [self._create_client(config) for config in self.api_configs]

        elif ServeConfig.api_key:
            self.clients = [self._create_client({"api_key": ServeConfig.api_key,
                                                 "base_url": ServeConfig.base_url})]
        else:
            raise ValueError("api_configs must be a list of dictionaries with 'api_key' and 'base_url' keys")
        self.client = self.clients[self.client_index]
        self.cache_expire_after_seconds = cache_expire_after_seconds
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

    def _create_client(self, config: dict) -> AsyncOpenAI:
        return AsyncOpenAI(api_key=config['api_key'], base_url=config['base_url'])

    def rotate_client(self):
        self.client_index = (self.client_index + 1) % len(self.api_configs)
        self.client = self.clients[self.client_index]

    async def get_client(self):
        limiter = self.limiters[self.client_index]
        if not await limiter.check_limit():
            self.rotate_client()
            limiter = self.limiters[self.client_index]
        return self.client, limiter
