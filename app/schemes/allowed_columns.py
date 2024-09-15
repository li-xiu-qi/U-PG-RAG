from typing import List

partition_allowed_columns: List[str] = ["partition_name"]
file_allowed_columns: List[str] = ["file_name", "file_url", "file_type", "file_path"]
markdown_allowed_columns: List[str] = ["title", "content", "hash_key"]
document_allowed_columns: List[str] = ["title", "content", "hash_key"]
vector_allowed_columns: List[str] = ["query_or_chunk", "vector"]
token_allowed_columns: List[str] = ["token"]
rag_cache_allowed_columns: List[str] = ["query", "response"]
conversation_allowed_columns: List[str] = ["messages"]
response_record_allowed_columns: List[str] = ["input", "response"]
user_allowed_columns: List[str] = ["user_name", "account", "email", "phone", "role", "status"]
admin_allowed_columns: List[str] = ["admin_name", "account", "email", "phone", "role", "status"]
super_admin_allowed_columns: List[str] = ["super_admin_name", "account", "email", "phone", "role", "status"]
