from typing import List

from sqlalchemy import func, select

from app.crud.filter_utils.filters import FilterHandler


def build_search_query(db_model, search_columns: List[str], query_condition: str, filters: dict,
                       sort_by_rank: bool, filter_handler: FilterHandler):
    search_vector = func.to_tsvector('jiebacfg',
                                     func.concat_ws(' ', *[getattr(db_model, col) for col in search_columns]))
    search_query = func.to_tsquery('jiebacfg', query_condition)
    search_condition = search_vector.op('@@')(search_query)

    query = select(db_model).where(search_condition)

    filter_clause = filter_handler.create_filter_clause(filters)
    query = query.where(filter_clause)

    if sort_by_rank:
        rank_score = func.ts_rank(search_vector, search_query).label('rank_score')
        rank_position = func.row_number().over(order_by=rank_score.desc()).label('rank_position')
        query = query.add_columns(*db_model.__table__.columns, rank_position, rank_score).order_by(rank_score.desc())
    else:
        query = query.add_columns(*db_model.__table__.columns)

    return query