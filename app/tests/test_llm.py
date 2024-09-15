from app.serves.model_serves import AsyncLLM, LLMInput
import asyncio

from utils import find_project_root_and_load_dotenv

# 加载环境变量
find_project_root_and_load_dotenv("U-PG-RAG")

# 创建异步语言模型实例
llm = AsyncLLM()


async def main():
    # 创建消息对象列表
    message = [{"role": "user", "content": "你好"}]

    # 初始化 LLMInput 对象
    input_data = LLMInput(
        model_name="Qwen/Qwen2-7B-Instruct",
        task_input=message
    )

    try:
        # 获取响应
        response = await llm(input_data)
        print(response)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
