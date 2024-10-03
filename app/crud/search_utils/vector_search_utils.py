from sqlalchemy import func, select, and_, Float


def build_vector_search_query(db_model, query_vector,
                              filter_conditions: list, offset: int,
                              limit: int, threshold: float = None):
    columns_to_select = [col for col in db_model.__table__.columns if col.name != 'vector']
    query = select(db_model).add_columns(*columns_to_select)

    if filter_conditions:
        query = query.where(and_(*filter_conditions))

    similarity_score = (1 - db_model.vector.op('<=>', return_type=Float)(query_vector)).label('rank_score')
    rank_position = func.row_number().over(order_by=similarity_score.desc()).label('rank_position')

    query = query.add_columns(similarity_score, rank_position).order_by(rank_position).offset(offset).limit(limit)

    if threshold is not None:
        query = query.where(similarity_score >= threshold)

    return query
