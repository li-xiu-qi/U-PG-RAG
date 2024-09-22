from typing import Set

partition_disallowed_columns: Set[str] = {"partition_id"}
file_disallowed_columns: Set[str] = {"file_id"}
markdown_disallowed_columns: Set[str] = {"markdown_id"}
document_disallowed_columns: Set[str] = {"document_id"}
vector_disallowed_columns: Set[str] = {"vector_id"}
token_disallowed_columns: Set[str] = {"token_id"}
rag_cache_disallowed_columns: Set[str] = {"cache_id"}
conversation_disallowed_columns: Set[str] = {"conversation_id"}
response_record_disallowed_columns: Set[str] = {"record_id"}
user_disallowed_columns: Set[str] = {"password"}
admin_disallowed_columns: Set[str] = {"password"}
super_admin_disallowed_columns: Set[str] = {"password"}
