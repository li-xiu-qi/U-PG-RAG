# vector_model_example.py

vector_base_examples = [
    {
        "query_or_chunk": "example query",
        "category": "example category",
        "partition_id": None,
        "file_id": None,
        "md_id": None,
        "doc_id": None,
        "vector": None
    },
    {
        "query_or_chunk": "another query",
        "category": "another category",
        "partition_id": 2,
        "file_id": 3,
        "md_id": 4,
        "doc_id": 5,
        "vector": [0.1, 0.2, 0.3]
    }
]

vector_update_examples = [
    {
        "id": 1,
        "query_or_chunk": "updated query",
        "vector": None,
        "category": "updated category",
        "partition_id": None,
        "file_id": None,
        "md_id": None,
        "doc_id": None
    },
    {
        "id": 2,
        "query_or_chunk": "another updated query",
        "vector": [0.4, 0.5, 0.6],
        "category": "another updated category",
        "partition_id": 3,
        "file_id": 4,
        "md_id": 5,
        "doc_id": 6
    }
]

response_vector_examples = [
    {
        "id": 1,
        "query_or_chunk": "example query",
        "category": "example category",
        "partition_id": 1,
        "file_id": 1,
        "md_id": 1,
        "doc_id": 1,
        "create_at": "2023-01-01T00:00:00",
        "update_at": "2023-01-01T00:00:00"
    },
    {
        "id": 2,
        "query_or_chunk": "another query",
        "category": "another category",
        "partition_id": 2,
        "file_id": 2,
        "md_id": 2,
        "doc_id": 2,
        "create_at": "2023-02-01T00:00:00",
        "update_at": "2023-02-01T00:00:00"
    }
]

vector_keyword_search_examples = [
    {
        "keywords": ["example"],
        "search_columns": ["query_or_chunk"],
        "sort_by_rank": True,
        "offset": 0,
        "limit": 20,
        "filters": {
            "partition_id": None,
            "file_id": None,
            "md_id": None,
            "doc_id": None
        },
        "exact_match": False
    },
    {
        "keywords": ["another"],
        "search_columns": ["query_or_chunk"],
        "sort_by_rank": False,
        "offset": 10,
        "limit": 30,
        "filters": {
            "partition_id": 1,
            "file_id": 2,
            "md_id": 3,
            "doc_id": 4
        },
        "exact_match": True
    }
]

search_vector_response_examples = [
    {
        "id": 1,
        "query_or_chunk": "example query",
        "category": "example category",
        "partition_id": 1,
        "file_id": 1,
        "md_id": 1,
        "doc_id": 1,
        "vector": [0.1, 0.2, 0.3],
        "create_at": "2023-01-01T00:00:00",
        "update_at": "2023-01-01T00:00:00",
        "rank_score": 0.95,
        "rank_position": 1
    },
    {
        "id": 2,
        "query_or_chunk": "another query",
        "category": "another category",
        "partition_id": 2,
        "file_id": 2,
        "md_id": 2,
        "doc_id": 2,
        "vector": [0.4, 0.5, 0.6],
        "create_at": "2023-02-01T00:00:00",
        "update_at": "2023-02-01T00:00:00",
        "rank_score": 0.85,
        "rank_position": 2
    }
]

vector_single_item_examples = [
    {
        "id": 1,
        "filters": {
            "partition_id": None,
            "file_id": None,
            "md_id": None,
            "doc_id": None
        }
    },
    {
        "id": 2,
        "filters": {
            "partition_id": 1,
            "file_id": 2,
            "md_id": 3,
            "doc_id": 4
        }
    }
]

vector_pagination_examples = [
    {
        "offset": 0,
        "limit": 20,
        "filters": {
            "partition_id": None,
            "file_id": None,
            "md_id": None,
            "doc_id": None
        }
    },
    {
        "offset": 10,
        "limit": 30,
        "filters": {
            "partition_id": 1,
            "file_id": 2,
            "md_id": 3,
            "doc_id": 4
        }
    }
]

vector_search_examples = [
    {
        "query_or_chunk": "example query",
        "offset": 0,
        "limit": 20,
        "filters": {
            "partition_id": None,
            "file_id": None,
            "md_id": None,
            "doc_id": None
        },
        "vector": None
    },
    {
        "query_or_chunk": "another query",
        "offset": 10,
        "limit": 30,
        "filters": {
            "partition_id": 1,
            "file_id": 2,
            "md_id": 3,
            "doc_id": 4
        },
        "vector": [0.1, 0.2, 0.3]
    }
]

hybrid_search_model_examples = [
    {
        "query_or_chunk": "example query",
        "keywords": ["example"],
        "search_columns": ["query_or_chunk"],
        "sort_by_rank": True,
        "offset": 0,
        "limit": 20,
        "exact_match": False,
        "vector": None,
        "k": 1,
        "filters": {
            "partition_id": None,
            "file_id": None,
            "md_id": None,
            "doc_id": None
        }
    },
    {
        "query_or_chunk": "another query",
        "keywords": ["another"],
        "search_columns": ["query_or_chunk"],
        "sort_by_rank": False,
        "offset": 10,
        "limit": 30,
        "exact_match": True,
        "vector": [0.1, 0.2, 0.3],
        "k": 5,   "filters": {
            "partition_id": 1,
            "file_id": 2,
            "md_id": 3,
            "doc_id": 4
        }
    }
]

search_hybrid_response_examples = [
    {
        "id": 1,
        "query_or_chunk": "example query",
        "category": "example category",
        "partition_id": 1,
        "file_id": 1,
        "md_id": 1,
        "doc_id": 1,
        "create_at": "2023-01-01T00:00:00",
        "update_at": "2023-01-01T00:00:00",
        "rank_score": 0.95,
        "rank_position": 1
    },
    {
        "id": 2,
        "query_or_chunk": "another query",
        "category": "another category",
        "partition_id": 2,
        "file_id": 2,
        "md_id": 2,
        "doc_id": 2,
        "create_at": "2023-02-01T00:00:00",
        "update_at": "2023-02-01T00:00:00",
        "rank_score": 0.85,
        "rank_position": 2
    }
]