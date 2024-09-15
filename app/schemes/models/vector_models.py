from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from app.schemes.base_models import KeywordSearchModel
from app.schemes.model_filters import DocumentFilter
from app.schemes.model_examples.vector_model_example import (
    vector_base_examples,
    vector_update_examples,
    response_vector_examples,
    vector_keyword_search_examples,
    search_vector_response_examples,
    vector_single_item_examples,
    vector_pagination_examples,
    vector_search_examples,
    hybrid_search_model_examples,
    search_hybrid_response_examples
)


# 定义 VectorBase 模型
class VectorBase(BaseModel):
    query_or_chunk: str
    category: Optional[str] = None
    partition_id: Optional[int] = None
    file_id: Optional[int] = None
    md_id: Optional[int] = None
    doc_id: Optional[int] = None
    vector: Optional[List[float]] = None

    model_config = {
        "json_schema_extra": {
            "examples": vector_base_examples
        }
    }


# 定义 VectorCreate 模型
class VectorCreate(VectorBase):
    pass


# 定义 VectorUpdate 模型
class VectorUpdate(BaseModel):
    id: int
    query_or_chunk: Optional[str] = None
    vector: Optional[List[float]] = None
    category: Optional[str] = None
    partition_id: Optional[int] = None
    file_id: Optional[int] = None
    md_id: Optional[int] = None
    doc_id: Optional[int] = None

    model_config = {
        "json_schema_extra": {
            "examples": vector_update_examples
        }
    }


# 定义 ResponseVector 模型
class ResponseVector(BaseModel):
    id: int
    query_or_chunk: str
    category: Optional[str] = None
    partition_id: Optional[int] = None
    file_id: Optional[int] = None
    md_id: Optional[int] = None
    doc_id: Optional[int] = None
    create_at: datetime
    update_at: datetime

    model_config = {
        "json_schema_extra": {
            "examples": response_vector_examples
        }
    }


# 定义 VectorKeywordSearch 模型
class VectorKeywordSearch(KeywordSearchModel):
    search_columns: List[str] = ["query_or_chunk"]
    filters: Optional[DocumentFilter] = None

    model_config = {
        "json_schema_extra": {
            "examples": vector_keyword_search_examples
        }
    }


# 定义 SearchVectorResponse 模型
class SearchVectorResponse(BaseModel):
    id: int
    query_or_chunk: str
    category: Optional[str] = None
    partition_id: Optional[int] = None
    file_id: Optional[int] = None
    md_id: Optional[int] = None
    doc_id: Optional[int] = None
    create_at: datetime
    update_at: datetime
    rank_score: Optional[float] = None
    rank_position: Optional[int] = None

    model_config = {
        "json_schema_extra": {
            "examples": search_vector_response_examples
        }
    }


# 定义 VectorSingleItem 模型
class VectorSingleItem(BaseModel):
    id: int
    filters: Optional[DocumentFilter] = None

    model_config = {
        "json_schema_extra": {
            "examples": vector_single_item_examples
        }
    }


# 定义 VectorPagination 模型
class VectorPagination(BaseModel):
    offset: int
    limit: int
    filters: Optional[DocumentFilter] = None

    model_config = {
        "json_schema_extra": {
            "examples": vector_pagination_examples
        }
    }


# 定义 VectorSearch 模型
class VectorSearch(BaseModel):
    query_or_chunk: str
    offset: int = 0
    limit: int = 20
    filters: Optional[DocumentFilter] = None
    vector: Optional[List[float]] = None

    model_config = {
        "json_schema_extra": {
            "examples": vector_search_examples
        }
    }


# 定义 HybridSearchModel 模型
class HybridSearchModel(BaseModel):
    query_or_chunk: str
    keywords: List[str]
    search_columns: Optional[List[str]] = ["query_or_chunk"]
    sort_by_rank: Optional[bool] = True
    offset: Optional[int] = 0
    limit: Optional[int] = 20
    exact_match: bool = False
    vector: Optional[List[float]] = None
    k: Optional[int] = 1
    filters: Optional[DocumentFilter] = None


    model_config = {
        "json_schema_extra": {
            "examples": hybrid_search_model_examples
        }
    }


# 定义 SearchHybridResponse 模型
class SearchHybridResponse(BaseModel):
    id: int
    query_or_chunk: str
    category: Optional[str] = None
    partition_id: Optional[int] = None
    file_id: Optional[int] = None
    md_id: Optional[int] = None
    doc_id: Optional[int] = None
    create_at: datetime
    update_at: datetime
    rank_score: Optional[float] = None
    rank_position: Optional[int] = None

    model_config = {
        "json_schema_extra": {
            "examples": search_hybrid_response_examples
        }
    }


# 定义 get_vector 函数
def get_vector(
        id: int,
        partition_id: Optional[int] = None,
        file_id: Optional[int] = None,
        md_id: Optional[int] = None,
        doc_id: Optional[int] = None):
    filters = DocumentFilter(
        partition_id=partition_id,
        file_id=file_id,
        md_id=md_id,
        doc_id=doc_id
    )
    return VectorSingleItem(id=id, filters=filters)


# 定义 get_vectors 函数
def get_vectors(
        offset: Optional[int] = 0,
        limit: Optional[int] = 20,
        partition_id: Optional[int] = None,
        file_id: Optional[int] = None,
        md_id: Optional[int] = None,
        doc_id: Optional[int] = None):
    filters = DocumentFilter(
        partition_id=partition_id,
        file_id=file_id,
        md_id=md_id,
        doc_id=doc_id)

    return VectorPagination(offset=offset, limit=limit, filters=filters)