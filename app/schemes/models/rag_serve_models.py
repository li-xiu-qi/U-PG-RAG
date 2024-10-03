from datetime import datetime
from typing import Any

from pydantic import BaseModel
from typing_extensions import Literal


class RAGServeModel(BaseModel):
    """
    query: 用户问题
    limit: 限制检索结果数量
    use_vector_search: 是否使用向量检索
    use_keyword_search: 是否使用关键词检索
    rerank: 是否使用rerank
    keyword_weight: 关键词检索权重
    vector_weight: 向量检索权重
    recursive_query: 是否使用递归查询
    paragraph_number_ranking: 是否使用段落数量排序
    filter_count: 过滤检索结果数量，-1表示不过滤
    """
    query: str
    limit: int = 15
    use_vector_search: bool = True
    use_keyword_search: bool = True
    rerank: bool = False
    keyword_weight: float = 7
    vector_weight: float = 3
    recursive_query: bool = False
    paragraph_number_ranking: bool = False
    filter_count: int = -1


class RAGStreamResponse(BaseModel):
    data_type: Literal["answer", "retrieval",
    "web_search", "md_content"
    ]
    result: Any


class RAGResponse(BaseModel):
    response: str
    time: float
    retrieval_documents: list
