import hashlib
from typing import List

class WebSearchProcessor:
    def __init__(self):
        pass

    def simhash(self, document: str) -> int:
        tokens = document.split()
        v = [0] * 128
        for token in tokens:
            token_hash = int(hashlib.md5(token.encode('utf8')).hexdigest(), 16)
            for i in range(128):
                bitmask = 1 << i
                if token_hash & bitmask:
                    v[i] += 1
                else:
                    v[i] -= 1
        fingerprint = 0
        for i in range(128):
            if v[i] >= 0:
                fingerprint |= 1 << i
        return fingerprint

    def hamming_distance(self, hash1: int, hash2: int) -> int:
        x = hash1 ^ hash2
        tot = 0
        while x:
            tot += 1
            x &= x - 1
        return tot

    def filter_similar_documents(self, documents: List[str], threshold: int = 10) -> List[str]:
        hashes = [self.simhash(doc) for doc in documents]

        unique_documents = []
        for i in range(len(documents)):
            is_unique = True
            for j in range(i):
                if self.hamming_distance(hashes[i], hashes[j]) < threshold:
                    is_unique = False
                    break
            if is_unique:
                unique_documents.append(documents[i])

        return unique_documents

# 示例用法
processor = WebSearchProcessor()
documents = ["文档1内容", "文档1内容sdfasf ", "文档2内容", "文档3内容"]
filtered_documents = processor.filter_similar_documents(documents)
print(filtered_documents)