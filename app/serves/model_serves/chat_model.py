import logging
from typing import TypeVar, AsyncGenerator, Literal

from openai import AsyncClient
from pydantic import BaseModel

from app.serves.model_serves.cache_manager import llm_cached_call
from app.serves.model_serves.client_manager import ClientManager
from app.serves.model_serves.rag_model import RAGModel
from app.serves.model_serves.types import LLMInput, LLMOutput, Message
from config import ServeConfig

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

TInput = TypeVar('TInput', bound=BaseModel)
TOutput = TypeVar('TOutput', bound=BaseModel)


class ChatModel(RAGModel):

    async def ainvoke(self, model_name, user_input, system_input,
                      response_format: Literal["json"] | None = None) -> LLMOutput:
        logger.info("Invoking model: %s", model_name)
        messages = [Message(role="system", content=system_input),
                    Message(role="user", content=user_input)]
        input_data = LLMInput(name=model_name, input_content=messages)
        response = await self.chat(model_input=input_data, response_format=response_format)
        return response

    @llm_cached_call()
    async def chat(self, *, model_input: LLMInput, max_retries: int = 5,
                   response_format: Literal["json"] | None = None) -> LLMOutput:
        logger.info("Chat request for model: %s", model_input.name)

        async def chat_func(client: AsyncClient, limiter, model_input, response_format):
            if response_format:
                response_format = {"type": "json_object"}
            response = await client.chat.completions.create(
                model=model_input.name,
                messages=model_input.input_content,
                **model_input.set_param or {},
                response_format=response_format
            )

            total_tokens = response.usage.total_tokens
            limiter.update_limit_status(tokens=total_tokens)
            logger.debug("Chat response received with total tokens: %d", total_tokens)

            return LLMOutput(output=response.choices[0].message.content, total_tokens=total_tokens)

        response = await self._execute_with_retries(chat_func, model_input, max_retries=max_retries,
                                                    response_format=response_format)
        return response

    async def stream_chat(self, model_input: LLMInput, max_retries: int = 5) -> AsyncGenerator[LLMOutput, None]:
        logger.info("Streaming chat for model: %s", model_input.name)

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

    async def _handle_async_generator(self, async_gen):
        async for item in async_gen:
            yield item


