from fastapi import APIRouter

from app.apis.routers.admin_crud_router import AdminCRUDRouter
from app.apis.routers.cache_crud_router import CacheCRUDRouter
from app.apis.routers.data_crud_router import DataCRUDRouter
from app.apis.routers.user_cu_router import UserCURouter
from app.apis.routers.vector_crud_router import VectorRouter
from app.db import db_models, db_unique_keys
from app.schemes import allowed_columns
from app.schemes.models import cache_models, user_models, chat_models, data_models, partition_models, vector_models

# Admin Router
admin_router = APIRouter(prefix="/xiaoke_admin", tags=["后台管理"])
AdminCRUDRouter(
    router=admin_router,
    dbmodel=db_models.User,
    response_model=user_models.ResponseAdmin,
    create_model=user_models.AdminCreate,
    update_model=user_models.AdminUpdate,
    get_item=user_models.get_user,
    get_items=user_models.get_users,
    keyword_search_model=user_models.AdminKeywordSearch,
    allowed_columns=allowed_columns.user_allowed_columns,
    unique_keys=db_unique_keys.user_unique_key,
)

# RAGCache Router
rag_cache_router = APIRouter(prefix="/rag_cache", tags=["RAGCache查询"])
CacheCRUDRouter(
    router=rag_cache_router,
    dbmodel=db_models.RAGCache,
    response_model=cache_models.ResponseRAGCache,
    create_model=cache_models.RAGCacheCreate,
    update_model=cache_models.RAGCacheUpdate,
    get_item=cache_models.get_rag_cache,
    get_items=cache_models.get_rag_caches,
    keyword_search_model=cache_models.RAGCacheKeywordSearch,
    search_response_model=cache_models.SearchRAGCacheResponse,
    allowed_columns=allowed_columns.rag_cache_allowed_columns,
    unique_keys=db_unique_keys.rag_cache_unique_key,
)

# Conversation Router
conversation_router = APIRouter(prefix="/conversation", tags=["会话查询"])
DataCRUDRouter(
    router=conversation_router,
    dbmodel=db_models.Conversation,
    response_model=chat_models.ResponseConversation,
    create_model=chat_models.ConversationCreate,
    update_model=chat_models.ConversationUpdate,
    get_item=chat_models.get_conversation,
    get_items=chat_models.get_conversations,
    keyword_search_model=chat_models.ConversationKeywordSearch,
    search_response_model=chat_models.SearchConversationResponse,
    allowed_columns=allowed_columns.conversation_allowed_columns,
    unique_keys=db_unique_keys.conversation_unique_key,
)

# Response Record Router
response_record_router = APIRouter(prefix="/response_record", tags=["响应记录查询"])
DataCRUDRouter(
    router=response_record_router,
    dbmodel=db_models.ResponseRecord,
    response_model=chat_models.ResponseResponseRecord,
    create_model=chat_models.ResponseRecordCreate,
    update_model=chat_models.ResponseRecordUpdate,
    get_item=chat_models.get_response_record,
    get_items=chat_models.get_response_records,
    keyword_search_model=chat_models.ResponseRecordKeywordSearch,
    search_response_model=chat_models.SearchResponseRecordResponse,
    allowed_columns=allowed_columns.response_record_allowed_columns,
    unique_keys=db_unique_keys.response_record_unique_key,
)

# Markdown Router
markdown_router = APIRouter(prefix="/markdown", tags=["Markdown查询"])
DataCRUDRouter(
    router=markdown_router,
    dbmodel=db_models.Markdown,
    response_model=data_models.ResponseMarkdown,
    create_model=data_models.MarkdownCreate,
    update_model=data_models.MarkdownUpdate,
    get_item=data_models.get_markdown,
    get_items=data_models.get_markdowns,
    keyword_search_model=data_models.MarkdownKeywordSearch,
    search_response_model=data_models.SearchMarkdownResponse,
    allowed_columns=allowed_columns.markdown_allowed_columns,
    unique_keys=db_unique_keys.markdown_unique_key,
)

# Document Router
document_router = APIRouter(prefix="/document", tags=["文档查询"])
DataCRUDRouter(
    router=document_router,
    dbmodel=db_models.Document,
    response_model=data_models.ResponseDocument,
    create_model=data_models.DocumentCreate,
    update_model=data_models.DocumentUpdate,
    get_item=data_models.get_document,
    get_items=data_models.get_documents,
    keyword_search_model=data_models.DocumentKeywordSearch,
    search_response_model=data_models.SearchDocumentResponse,
    allowed_columns=allowed_columns.document_allowed_columns,
    unique_keys=db_unique_keys.document_unique_key,
)

# Partition Router
partition_router = APIRouter(prefix="/partition", tags=["分区管理"])
DataCRUDRouter(
    router=partition_router,
    dbmodel=db_models.Partition,
    response_model=partition_models.ResponsePartition,
    create_model=partition_models.PartitionCreate,
    update_model=partition_models.PartitionUpdate,
    get_item=partition_models.get_partition,
    get_items=partition_models.get_partitions,
    keyword_search_model=partition_models.PartitionKeywordSearch,
    search_response_model=partition_models.SearchPartitionResponse,
    allowed_columns=allowed_columns.partition_allowed_columns,
    unique_keys=db_unique_keys.partition_unique_key,
)

# User Router
user_router = APIRouter(prefix="/user", tags=["用户管理"])
UserCURouter(
    router=user_router,
    dbmodel=db_models.User,
    response_model=user_models.ResponseUser,
    create_model=user_models.UserCreate,
    update_model=user_models.UserUpdate,
    unique_keys=db_unique_keys.user_unique_key,
)

# Vector Router
vector_router = APIRouter(prefix="/vector", tags=["向量数据管理"])

router = VectorRouter(
    router=vector_router,
    dbmodel=db_models.Vector,
    response_model=vector_models.ResponseVector,
    create_model=vector_models.VectorCreate,
    update_model=vector_models.VectorUpdate,
    get_item=vector_models.get_vector,
    get_items=vector_models.get_vectors,
    keyword_search_model=vector_models.VectorKeywordSearch,
    search_response_model=vector_models.SearchVectorResponse,
    vector_search_model=vector_models.VectorSearch,
    hybrid_search_model=vector_models.HybridSearchModel,
    allowed_columns=allowed_columns.vector_allowed_columns,
    unique_keys=db_unique_keys.vector_unique_key,
)