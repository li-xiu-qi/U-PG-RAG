from typing import List, Type, TypeVar
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.search_utils.search import search
from app.crud.search_utils.vector_search import vector_search
from app.crud.filter_utils.filters import FilterHandler

T = TypeVar('T', bound=BaseModel)


async def hybrid_search(
        db: AsyncSession,
        db_model: Type[T],
        model: BaseModel,
        filter_handler: FilterHandler,
) -> List[Type]:
    k = model.k
    vector_results = await vector_search(db, db_model, model, filter_handler)
    keyword_results = await search(db, db_model, model, filter_handler)

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
    scores = [1.0 / (k + vector_rank) + 1.0 / (k + keyword_rank) for vector_rank, keyword_rank in
              zip(vector_ranks, keyword_ranks)]

    for i, item in enumerate(combined_results.values()):
        item['score'] = scores[i]

    sorted_results = sorted(combined_results.values(), key=lambda x: x['score'], reverse=True)

    return [item['result'] for item in sorted_results]