import hashlib
import logging
import time
from typing import List, Optional

import faiss
import numpy as np

from app.serves.model_serves.embedding_model import EmbeddingModel
from app.serves.model_serves.types import EmbeddingInput

logger = logging.getLogger(__name__)


# 文档类，包含文档ID、内容、嵌入向量和元数据
class Document:
    def __init__(self, doc_id: str, content: str, embedding: np.ndarray, metadata: dict | None = None):
        self.doc_id = doc_id
        self.content = content
        self.embedding = embedding
        self.metadata = metadata or {}


# 内存向量搜索类
class MemoryVectorSearch:
    def __init__(self, model_name: str, embedding_model: EmbeddingModel = None, use_index: bool = True):
        self.index = None  # Faiss索引
        self.docstore = {}  # 文档存储
        self.index_to_docstore_id = {}  # 索引到文档ID的映射
        self.embedding_model = embedding_model  # 嵌入模型
        self.model_name = model_name  # 模型名称
        self.use_index = use_index  # 是否使用索引的标志

    # 获取嵌入输入
    def _get_embedding_input(self, documents: List[str] | str) -> EmbeddingInput:
        if isinstance(documents, str):
            documents = [documents]
        return EmbeddingInput(name=self.model_name, input_content=documents)

    # 添加文档
    async def add_documents(self, documents: List[str],
                            ids: Optional[List[str]] = None,
                            metadata: dict | None = None) -> List[str]:
        if len(documents) < 1:
            logger.warning("没有要添加的文档。")
            return []
        logger.debug(f"添加文档: {documents}")

        start_time = time.time()

        # 获取嵌入结果并标准化嵌入向量
        embedding_result = await self.embedding_model.embed_func(model_input=self._get_embedding_input(documents))
        embeddings = [embedding / np.linalg.norm(embedding) for embedding in embedding_result.output]

        if self.use_index:
            if self.index is None:
                self.index = faiss.IndexFlatIP(len(embeddings[0]))  # 创建Faiss索引
                logger.info("创建了新的Faiss索引。")
            self.index.add(np.array(embeddings, dtype=np.float32))  # 添加嵌入向量到索引
            logger.info("将嵌入向量添加到Faiss索引。")

        end_time = time.time()
        logger.info(f"索引构建耗时: {end_time - start_time:.2f} 秒。")

        new_ids = []
        for text, embedding in zip(documents, embeddings):
            doc_id = hashlib.md5(text.encode('utf-8')).hexdigest()
            if doc_id not in self.docstore:  # 确保不重复添加文档
                self.docstore[doc_id] = Document(doc_id, text, embedding, metadata=metadata)
                new_ids.append(doc_id)
                logger.debug(f"存储了ID为: {doc_id} 的文档。")

        # 仅在有新文档时更新索引
        if new_ids:
            self.index_to_docstore_id.update(
                {i: doc_id for i, doc_id in enumerate(new_ids, start=len(self.index_to_docstore_id))})
            logger.info("更新了索引到文档ID的映射。")
        return new_ids

    # 最大边际相关性搜索
    async def mmr(self, query: str, top_k: int = 30, fetch_k: int = 50,
                  lambda_factor: float = 0.95) -> List[Document]:
        logger.info(f"执行MMR搜索，查询: {query}")
        embedding_result = await self.embedding_model.embed_query(model_input=self._get_embedding_input(query))
        vector = np.array([embedding_result.output[0]], dtype=np.float32)
        vector /= np.linalg.norm(vector)  # 标准化向量

        if self.use_index:
            scores, indices = self.index.search(vector, fetch_k)  # 在索引中搜索
            logger.debug(f"搜索得分: {scores}, 索引: {indices}")
            embeddings = [self.index.reconstruct(int(index)) for index in indices[0] if index != -1]
        else:
            embeddings = [doc.embedding for doc in self.docstore.values()]  # 暴力搜索
            indices = np.argsort([np.dot(vector, emb) for emb in embeddings])[-fetch_k:]

        mmr_indices = await self.maximal_marginal_relevance(vector[0], embeddings, lambda_factor=lambda_factor)
        documents = [self.docstore[self.index_to_docstore_id[index]] for index in mmr_indices[:top_k]]
        logger.debug(f"MMR搜索结果: {documents}")
        return documents

    # 计算最大边际相关性
    async def maximal_marginal_relevance(self, query_embedding: np.ndarray, embeddings: List[np.ndarray],
                                         lambda_factor: float) -> List[int]:
        logger.debug("计算MMR索引。")
        selected_indices = []
        selected_indices.append(np.argmax([np.dot(query_embedding, emb) for emb in embeddings]))
        while len(selected_indices) < len(embeddings):
            remaining_indices = [i for i in range(len(embeddings)) if i not in selected_indices]
            mmr_scores = []
            for index in remaining_indices:
                similarity_to_query = np.dot(query_embedding, embeddings[index])
                similarity_to_selected = max(
                    [np.dot(embeddings[index], embeddings[selected_index]) for selected_index in
                     selected_indices])
                mmr_score = lambda_factor * similarity_to_query - (
                        1 - lambda_factor) * similarity_to_selected
                mmr_scores.append((mmr_score, index))
            selected_indices.append(max(mmr_scores)[1])
        logger.debug(f"MMR选择的索引: {selected_indices}")
        return selected_indices
