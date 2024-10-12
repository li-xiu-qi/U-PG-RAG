from typing import List

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import jaccard_score


class WebSearchProcessor:
    def __init__(self):
        self.vectorizer = CountVectorizer(binary=True)

    def filter_similar_documents(self, documents: List[str], threshold: float = 0.5) -> List[str]:
        # 将文档进行向量化
        binary_matrix = self.vectorizer.fit_transform(documents).toarray()

        # 计算文档之间的 Jaccard 相似度
        unique_documents = []
        for i in range(len(documents)):
            is_unique = True
            for j in range(i):
                score = jaccard_score(binary_matrix[i], binary_matrix[j])
                print(score)
                if score > threshold:
                    is_unique = False
                    break
            if is_unique:
                unique_documents.append(documents[i])

        return unique_documents


# 示例用法
processor = WebSearchProcessor()
documents = ["文档1内容fklsajdfljskaldjfjkfjsdfjl", "文档1内容fklsajdfljskaldjfjkfjsdfjl文档1内容的副本", "文档2文档1内容fklsajdfljskaldjfjkfjsdfjl内容", "文档3文档1内容fklsajdfljskaldjfjkfjsdfjl内容"]
filtered_documents = processor.filter_similar_documents(documents)
print(filtered_documents)
