import asyncio

from app.serves.model_serves.client_manager import ClientManager
from app.serves.model_serves.rag_model import RAG
from app.serves.model_serves.types import LLMInput, EmbeddingInput

from rag_config import embedding_api_configs

# 加载环境变量

client = ClientManager(api_configs=embedding_api_configs)
rag = RAG(client_manager=client)


async def main():
    # 创建消息对象列表
    message = [{"role": "user", "content": "你好"}]

    # 初始化 LLMInput 对象
    input_data = LLMInput(
        name="THUDM/glm-4-9b-chat",
        input_content=message
    )

    # 测试非流式聊天
    response = await rag.chat(input_data)
    print(response)

    # 测试流式聊天
    async for result in rag.stream_chat(input_data):
        print(f"output='{result.output}' total_tokens={result.total_tokens}")

    # 测试嵌入
    embed_input_data = EmbeddingInput(
        name="BAAI/bge-m3",
        input_content=["你好"]
    )
    response = await rag.embedding(embed_input_data)
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
