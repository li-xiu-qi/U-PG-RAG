from typing import TypeVar

import numpy as np
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.filter_utils.filters import FilterHandler
from app.crud.search_utils.search import search
from app.crud.search_utils.vector_search import vector_search
from model_constant import get_rerank_model

T = TypeVar('T', bound=BaseModel)


async def sort_hybrid_results(
        model: BaseModel,
        vector_results: list,
        keyword_results: list
) -> list:
    k = model.k
    vector_weight = model.vector_weight
    keyword_weight = model.keyword_weight

    total_weight = vector_weight + keyword_weight
    vector_weight /= total_weight
    keyword_weight /= total_weight

    combined_results = {}

    for rank, result in enumerate(vector_results, start=1):
        combined_results[result.id] = {
            'result': result,
            'vector_rank': rank,
            'keyword_rank': None
        }

    for rank, result in enumerate(keyword_results, start=1):
        if result.id in combined_results:
            combined_results[result.id]['keyword_rank'] = rank
        else:
            combined_results[result.id] = {
                'result': result,
                'vector_rank': None,
                'keyword_rank': rank
            }

    vector_ranks = [item['vector_rank'] if item['vector_rank'] is not None else float('inf') for item in
                    combined_results.values()]
    keyword_ranks = [item['keyword_rank'] if item['keyword_rank'] is not None else float('inf') for item in
                     combined_results.values()]
    scores = [vector_weight / (k + vector_rank) + keyword_weight / (k + keyword_rank) for vector_rank, keyword_rank in
              zip(vector_ranks, keyword_ranks)]

    for i, item in enumerate(combined_results.values()):
        item['score'] = scores[i]

    sorted_results = sorted(combined_results.values(), key=lambda x: x['score'], reverse=True)

    return [item['result'] for item in sorted_results]


async def sort_rerank_results(
        model: BaseModel,
        vector_results: list,
        keyword_results: list,
        chunk_size: int = 832,
        chunk_overlap: int = 32
) -> list:
    # 获取 vector_results 和 keyword_results 的并集，并去除重复的部分
    combined_results = {}
    combined_results.update({result.id: result for result in vector_results})
    combined_results.update({result.id: result for result in keyword_results})

    filtered_results = list(combined_results.values())

    query = model.page_content
    documents = [result.page_content for result in filtered_results]
    rerank_model = get_rerank_model()
    sorted_documents = await rerank_model.get_sorted_documents(query=query, documents=documents,
                                                               chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    sorted_results = [next(result for result in filtered_results if result.page_content == doc) for doc in
                      sorted_documents]

    return sorted_results


async def hybrid_search(
        db: AsyncSession,
        model: BaseModel,
        filter_handler: FilterHandler,
) -> list:
    use_vector_search = model.use_vector_search
    use_keyword_search = model.use_keyword_search
    vector_results = []
    keyword_results = []
    chunk_sizes = []
    chunk_overlaps = []
    if use_vector_search:
        vector_results = await vector_search(db, model, filter_handler)
        for result in vector_results:
            chunk_sizes.append(result.doc_metadata['chunk_size'])
            chunk_overlaps.append(result.doc_metadata['chunk_overlap'])

    if use_keyword_search:
        keyword_results = await search(db, model, filter_handler)
        for result in keyword_results:
            chunk_sizes.append(result.doc_metadata['chunk_size'])
            chunk_overlaps.append(result.doc_metadata['chunk_overlap'])
    max_chunk_size = max(chunk_sizes)
    min_chunk_overlap = min(chunk_overlaps)
    if model.rerank:
        rerank_results = await sort_rerank_results(model, vector_results, keyword_results, max_chunk_size,
                                                   min_chunk_overlap)
        if model.paragraph_number_ranking:
            rerank_results = await rank_by_paragraph_number(rerank_results, model.filter_count)
        return rerank_results
    elif use_vector_search and use_keyword_search:
        hybrid_results = await sort_hybrid_results(model, vector_results, keyword_results)
        if model.paragraph_number_ranking:
            hybrid_results = await rank_by_paragraph_number(hybrid_results, model.filter_count)
        return hybrid_results
    elif use_vector_search:
        return vector_results
    elif use_keyword_search:
        return keyword_results
    else:
        return []


async def rank_by_paragraph_number(chunks: list, filter_count: int):
    """
    一共取20个结果，先直接按照20过滤一遍
    接着按照document_id做一个分组，排序按照原来的顺序
    然后按照paragraph_number分别排序
    接着按照开始的是欧的id，拼接分别排序后的结果

    paragraph_number = document.doc_metadata['paragraph_number']
    :param chunks:
    :return:
    """
    # 一共取20个结果，先直接按照20过滤一遍
    if filter_count != -1:
        chunks = chunks[:filter_count]
    # 接着按照document_id做一个分组，给每一个组分别排序
    id_group = {}
    for chunk in chunks:
        id_group.setdefault(chunk.document_id, []).append(chunk)
    # 按照paragraph_number分别排序
    for _id, group in id_group.items():
        group.sort(key=lambda x: x.doc_metadata['paragraph_number'])
    # 按照开始的id，拼接分别排序后的结果
    sorted_chunks = []
    for _id in id_group.keys():
        sorted_chunks.extend(id_group[_id])
    return sorted_chunks
