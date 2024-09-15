# Python
import os
import random
import json
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any, List, Union, Dict

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pg_cache import AsyncPgCache

from app.serves.model_serves.model_utils.buffer import cached_call
from app.serves.model_serves.model_utils.limitator import RateLimiter, rate_limited_call

ModelOutput = TypeVar("ModelOutput", bound=Any)
ModelInput = TypeVar("ModelInput")


def load_from_json(file_path: str) -> List[Dict[str, str]]:
    with open(file_path, 'r') as file:
        return json.load(file)


class AsyncBaseModel(ABC, Generic[ModelOutput, ModelInput]):
    def __init__(self, task: str = "default",
                 buffer: AsyncPgCache = None,
                 api_configs: Union[str, List[Dict[str, str]]] = None,
                 max_requests_per_minute: int = None,
                 max_total_tokens_per_minute: int = None):
        self.task = task
        if api_configs is None:
            load_dotenv()
        if isinstance(api_configs, str):
            if os.path.isfile(api_configs):
                api_configs = load_from_json(api_configs)
            else:
                raise ValueError("Invalid file path for API configurations.")
        elif isinstance(api_configs, dict):
            api_configs = [api_configs]
        self.api_configs = api_configs or [{"api_key": os.getenv("API_KEY"), "base_url": os.getenv("BASE_URL")}]
        self.buffer = buffer
        self.limitator = RateLimiter(max_requests_per_minute=max_requests_per_minute,
                                     max_total_tokens_per_minute=max_total_tokens_per_minute)
        self.aclients = [AsyncOpenAI(api_key=config["api_key"], base_url=config["base_url"]) for config in
                         self.api_configs]
        self.enable_cache = buffer is not None
        self.client_index = 0  # 初始化客户端索引

    def get_client(self) -> AsyncOpenAI:
        client = self.aclients[self.client_index]
        self.client_index = (self.client_index + 1) % len(self.aclients)  # 更新索引以循环使用客户端
        return client

    @abstractmethod
    @cached_call()
    @rate_limited_call()
    async def __call__(self, task_input: ModelInput) -> ModelOutput:
        client = self.get_client()
        # 使用轮询选择的客户端进行调用
        return ModelOutput
