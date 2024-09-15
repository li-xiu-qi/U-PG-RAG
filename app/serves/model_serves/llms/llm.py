from app.serves.model_serves.base_models import AsyncBaseModel
from app.serves.model_serves.llms.llm_types import LLMInput, LLMOutput


class AsyncLLM(AsyncBaseModel[LLMInput, LLMOutput]):
    async def __call__(self, model_input: LLMInput) -> LLMOutput:
        response = await self.get_client().chat.completions.create(
            model=model_input.model_name,
            messages=model_input.task_input,
            **model_input.model_parameters if model_input.model_parameters else {},
        )
        task_output = response.choices[0].message.content
        total_tokens = response.usage.total_tokens
        return LLMOutput(task_output=task_output, total_tokens=total_tokens)
