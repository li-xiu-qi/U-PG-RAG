from typing import List, Type, TypeVar
from pydantic import BaseModel
from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

T = TypeVar('T', bound=BaseModel)


def sanitize_keywords(keywords: List[str]) -> List[str]:
    return [keyword.strip() for keyword in keywords if keyword.strip()]


def build_search_query(dbmodel: Type, search_columns: List[str], query_condition: str, filters: dict,
                       sort_by_rank: bool, exact_match: bool):
    if exact_match:
        search_condition = or_(*[getattr(dbmodel, col) == query_condition for col in search_columns])
    else:
        # 仅当数据库模型是 Conversation 并且字段是 messages 时，才将其转换为文本格式
        # 此处配置无效
        # TODO 修复messages字段的搜索
        # search_columns = [
        #     cast(getattr(dbmodel, col),
        #          Text) if dbmodel.__tablename__ == 'conversations' and col == 'messages' else getattr(dbmodel, col)
        #     for col in search_columns
        # ]
        search_vector = func.to_tsvector('jiebacfg',
                                         func.concat_ws(' ', *[getattr(dbmodel, col) for col in search_columns]))
        search_query = func.to_tsquery('jiebacfg', query_condition)
        search_condition = search_vector.op('@@')(search_query)

    query = select(dbmodel).where(search_condition)

    for key, value in filters.items():
        query = query.where(getattr(dbmodel, key) == value)

    if sort_by_rank and not exact_match:
        rank_score = func.ts_rank(search_vector, search_query).label('rank_score')
        rank_position = func.row_number().over(order_by=rank_score.desc()).label('rank_position')
        query = query.add_columns(*dbmodel.__table__.columns, rank_position, rank_score).order_by(rank_score.desc())
    else:
        query = query.add_columns(*dbmodel.__table__.columns)

    return query


async def search(
        db: AsyncSession,
        dbmodel: Type,
        model: BaseModel,
        allowed_columns: List[str],
) -> List[Type]:
    model_dict = model.model_dump(exclude_unset=True)
    if not model_dict:
        return []

    filters = model_dict.pop("filters", {})
    keywords = model_dict.pop("keywords", [])
    search_columns = model_dict.pop("search_columns", [])
    sort_by_rank = model_dict.pop("sort_by_rank", True)
    offset = model_dict.pop("offset", 0)
    limit = model_dict.pop("limit", 20)
    exact_match = model_dict.pop("exact_match", False)

    sanitized_keywords = sanitize_keywords(keywords)
    if not sanitized_keywords:
        return []

    if not search_columns:
        search_columns = allowed_columns

    search_columns = [col for col in search_columns if col in allowed_columns]
    if not search_columns:
        return []

    query_condition = ' & '.join(sanitized_keywords) if not exact_match else ' '.join(sanitized_keywords)

    query = build_search_query(dbmodel, search_columns, query_condition, filters, sort_by_rank, exact_match)
    query = query.offset(offset).limit(limit)

    try:
        result = await db.execute(query)
        results = result.all()
        return results
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        return []