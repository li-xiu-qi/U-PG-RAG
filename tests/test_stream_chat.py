from app.serves.model_serves.chat_model import ChatModel
from app.serves.model_serves.client_manager import ClientManager
from app.serves.model_serves.types import Message, LLMInput
from config import ServeConfig

if __name__ == "__main__":
    # 测试流式聊天
    import asyncio


    async def test_stream_chat():
        client = ClientManager(api_configs=ServeConfig.llm_api_configs)
        model = ChatModel(client_manager=client)
        messages = [Message(role="system", content="你是一个人工助手！"),
                    Message(role="user", content="你是谁？")]
        input_data = LLMInput(name="Qwen/Qwen2.5-7B-Instruct", input_content=messages)
        async for result in model.stream_chat(model_input=input_data):
            print(result.output)


    asyncio.run(test_stream_chat())