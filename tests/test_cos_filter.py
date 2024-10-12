import logging
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class WebSearchProcessor:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()

    def filter_similar_documents(self, documents: List[str], threshold: float = 0.8) -> List[str]:
        logger.info("过滤相似度高的文档。")

        # 将文档进行向量化
        tfidf_matrix = self.vectorizer.fit_transform(documents)

        # 计算文档之间的余弦相似度
        cosine_similarities = cosine_similarity(tfidf_matrix)
        print(cosine_similarities)

        # 过滤相似度高于阈值的文档
        unique_documents = []
        for i in range(len(documents)):
            is_unique = True
            for j in range(i):
                if cosine_similarities[i, j] > threshold:
                    is_unique = False
                    break
            if is_unique:
                unique_documents.append(documents[i])

        return unique_documents


# 示例用法
processor = WebSearchProcessor()
documents = ["文档1内容", "文档2内容", "文档3内容", "文档1内容"]
filtered_documents = processor.filter_similar_documents(documents)
print(filtered_documents)
