import asyncio

from app.serves.model_serves.client_manager import ClientManager
from app.serves.model_serves.rag_model import RAGModel
from app.serves.model_serves.types import EmbeddingInput
from rag_config import guiji_api_configs

# 加载环境变量

client = ClientManager(api_configs=guiji_api_configs)
rag = RAGModel(client_manager=client)


async def main():
    # 测试嵌入
    embed_input_data = EmbeddingInput(
        name="BAAI/bge-m3",
        input_content=[f"你好{_}" for _ in range(64)]
    )
    response = await rag.embedding(model_input=embed_input_data)
    print(len(response.output))

    # print(response)


if __name__ == "__main__":
    asyncio.run(main())
