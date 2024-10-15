import hashlib
from collections import Counter
from typing import List, Tuple


class LineParagraphFilter:
    def __init__(self):
        pass

    # 将文本按行分割，并返回每行的哈希值和长度
    def split_into_lines(self, text: str) -> List[Tuple[str, int]]:
        lines = text.splitlines()
        return [(self._hash_segment(line), len(line)) for line in lines]

    # 将文本按段落分割，并返回每段的哈希值和长度
    def split_into_paragraphs(self, text: str) -> List[Tuple[str, int]]:
        paragraphs = text.split('\n\n')
        return [(self._hash_segment(paragraph), len(paragraph)) for paragraph in paragraphs]

    # 计算文本片段的MD5哈希值
    def _hash_segment(self, segment: str) -> str:
        return hashlib.md5(segment.encode('utf-8')).hexdigest()

    # 计算两个文本片段列表之间的冗余率
    def calculate_redundancy(self, segments1: List[Tuple[str, int]], segments2: List[Tuple[str, int]]) -> float:
        counter1 = Counter([seg[0] for seg in segments1])
        counter2 = Counter([seg[0] for seg in segments2])
        common_segments = counter1 & counter2

        length_dict1 = {seg[0]: seg[1] for seg in segments1}
        length_dict2 = {seg[0]: seg[1] for seg in segments2}

        common_length = sum(min(length_dict1[seg], length_dict2[seg]) * count for seg, count in common_segments.items())
        total_length = sum(seg[1] for seg in segments1) + sum(seg[1] for seg in segments2)
        redundancy_rate = 2 * common_length / total_length
        return redundancy_rate

    # 过滤相似的文档，返回唯一的文档列表
    def filter_similar_documents(self, documents: List[str], threshold: float = 0.75, mode: str = 'paragraph') -> List[
        str]:
        if mode == 'line':
            split_func = self.split_into_lines
        elif mode == 'paragraph':
            split_func = self.split_into_paragraphs
        else:
            raise ValueError("Mode must be 'line' or 'paragraph'")

        segmented_docs = [split_func(doc) for doc in documents]
        unique_docs = []

        for i in range(len(documents)):
            is_unique = True
            for j in range(len(unique_docs)):
                redundancy_rate = self.calculate_redundancy(segmented_docs[i], segmented_docs[unique_docs[j]])
                if redundancy_rate > threshold:
                    if len(documents[i]) > len(documents[unique_docs[j]]):
                        unique_docs[j] = i
                    is_unique = False
                    break
            if is_unique:
                unique_docs.append(i)

        return [documents[i] for i in unique_docs]


if __name__ == '__main__':
    documents = [
        "This is the first line.\nThis is the second line.",
        "This is the first line.\nThis is another line.",
        "This is a completely different document."
    ]
    filter = LineParagraphFilter()
    unique_documents = filter.filter_similar_documents(documents, mode='line')
    print("Unique documents based on lines:", unique_documents)

    unique_documents = filter.filter_similar_documents(documents, mode='paragraph')
    print("Unique documents based on paragraphs:", unique_documents)
