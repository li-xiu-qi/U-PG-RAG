import aiohttp
from app.serves.model_serves.rag_model import RAGModel


class RerankModel(RAGModel):

    async def rerank_documents(self, query: str, documents: list, return_documents: bool = False,
                               max_chunks_per_doc: int = 832, overlap_tokens: int = 32) -> dict:
        url = "https://api.siliconflow.cn/v1/rerank"

        async def rerank_func(client, limiter):
            api_key = client.api_key
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

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    response_json = await response.json()
                    meta = response_json.get("meta", {})
                    tokens = meta.get("tokens", {})
                    total_tokens = tokens.get("input_tokens", 0)
                    limiter.update_limit_status(tokens=total_tokens)

                    return response_json

        return await self._execute_with_retries(rerank_func)

    async def get_sorted_documents(self, query: str, documents: list, return_documents: bool = False,
                                   max_chunks_per_doc: int = 832, overlap_tokens: int = 32) -> list:
        res = await self.rerank_documents(query, documents, return_documents, max_chunks_per_doc, overlap_tokens)

        results = res['results']
        sorted_documents = sorted(documents, key=lambda doc: next(
            item['relevance_score'] for item in results if documents.index(doc) == item['index']), reverse=True)

        return sorted_documents
