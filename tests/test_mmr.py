import asyncio

from app.serves.model_serves.client_manager import ClientManager
from app.serves.model_serves.mmr import MemoryVectorSearch
from tests.config import ServeConfig


async def test():
    from app.serves.model_serves.embedding_model import EmbeddingModel

    client_manager = ClientManager(api_configs=ServeConfig.embedding_api_configs)
    embedding_model = EmbeddingModel(client_manager=client_manager)
    faiss_search = MemoryVectorSearch(embedding_model=embedding_model, model_name="BAAI/bge-m3")
    texts = [
        "人工智能是一种模拟人类智能的技术。",
        "人工智能在医疗领域有广泛应用。",
        "区块链是一种分布式账本技朾。",
        "区块链在金融领域有重要应用。",
        "机器学习是人工智能的一个分支。",
        "深度学习是机器学习的一个分支。",
        "自然语言处理是人工智能的一个重要领域。",
        "计算机视觉是人工智能的一个重要领域。",
        "强化学习是一种机器学习方法。",
        "监督学习和无监督学习是机器学习的两大类。",
        "神经网络是深度学习的基础。",
        "卷积神经网络在图像处理领域有广泛应用。",
        "循环神经网络在自然语言处理领域有广泛应用。",
        "生成对抗网络是一种新型的神经网络。",
        "迁移学习是一种机器学习方法。",
        "联邦学习是一种分布式机器学习方法。",
        "大数据是人工智能的重要基础。",
        "云计算为人工智能提供了强大的计算能力。",
        "物联网与人工智能的结合带来了智能家居。",
        "智能机器人是人工智能的一个重要应用。",
    ]
    await faiss_search.add_texts(texts)  # 添加文本到索引
    query = "人工智能"
    documents = await faiss_search.mmr(query)  # 执行MMR搜索
    for doc in documents:
        print(f"Document ID: {doc.document_id}, Content: {doc.content}")


if __name__ == "__main__":
    asyncio.run(test())