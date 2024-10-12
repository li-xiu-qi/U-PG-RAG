import jieba
from collections import Counter
from typing import List


class TokenizerFilter:
    def __init__(self):
        self.tokenizer = jieba.Tokenizer()

    def tokenize(self, text: str) -> List[str]:
        tokens = self.tokenizer.cut(text)
        return list(tokens)

    def calculate_redundancy(self, tokens1: List[str], tokens2: List[str]) -> float:
        counter1 = Counter(tokens1)
        counter2 = Counter(tokens2)
        common_tokens = sum((counter1 & counter2).values())
        total_tokens = sum(counter1.values()) + sum(counter2.values())
        redundancy_rate = 2 * common_tokens / total_tokens
        return redundancy_rate

    def filter_similar_documents(self, documents: List[str], threshold: float = 0.75) -> List[str]:
        tokenized_docs = [self.tokenize(doc) for doc in documents]
        unique_docs = []

        for i in range(len(documents)):
            is_unique = True
            for j in range(len(unique_docs)):
                redundancy_rate = self.calculate_redundancy(tokenized_docs[i], tokenized_docs[unique_docs[j]])
                if redundancy_rate > threshold:
                    if len(documents[i]) > len(documents[unique_docs[j]]):
                        unique_docs[j] = i
                    is_unique = False
                    break
            if is_unique:
                unique_docs.append(i)

        return [documents[i] for i in unique_docs]


if __name__ == '__main__':
    documents = ["我爱北京天安门", "我爱北京故宫", "我爱北京的天安门"]
    filter = TokenizerFilter()
    unique_documents = filter.filter_similar_documents(documents)
    print(unique_documents)
