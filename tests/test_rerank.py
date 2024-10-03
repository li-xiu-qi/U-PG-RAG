import json
import requests

from config import ServeConfig


def rerank_documents(query,
                     documents,
                     api_key,
                     return_documents=False,
                     max_chunks_per_doc=1024,
                     overlap_tokens=80):
    url = "https://api.siliconflow.cn/v1/rerank"
    payload = {
        "model": "BAAI/bge-reranker-v2-m3",
        "query": query,
        "documents": documents,
        "return_documents": return_documents,
        "max_chunks_per_doc": max_chunks_per_doc,
        "overlap_tokens": overlap_tokens
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    response = requests.post(url, json=payload, headers=headers)
    print(json.dumps(response.json().get("meta").get("tokens").get("input_tokens"), indent=2))
    return response.json()


def get_sorted_documents(query, documents):
    api_key = ServeConfig.api_key
    res = rerank_documents(query, documents, api_key)

    results = res['results']
    sorted_documents = sorted(documents, key=lambda doc: next(
        item['relevance_score'] for item in results if documents.index(doc) == item['index']), reverse=True)

    return sorted_documents


query = "蔬菜呢？"
documents = ["我想要吃一个苹果", "不过我也想要吃一个香蕉", "他们都是水果吗", "为什么没有蔬菜？"]
sorted_docs = get_sorted_documents(query, documents)
print("Sorted documents based on relevance scores:")
print(sorted_docs)
