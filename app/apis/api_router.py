from fastapi import APIRouter

from app.apis.routers.admin_crud_router import AdminCRUDRouter
from app.apis.routers.base_crud_router import BaseCRUDRouter
from app.apis.routers.cache_crud_router import CacheCRUDRouter
from app.apis.routers.chunk_crud_router import ChunkRouter
from app.apis.routers.file_crud_router import FileCRUDRouter
from app.apis.routers.image_crud_router import ImageCRUDRouter
from app.apis.routers.user_cu_router import UserCURouter
from app.crud.admin_operation import AdminOperation
from app.crud.base_operation import BaseOperation
from app.crud.chunk_operation import ChunkOperation
from app.crud.file_operation import FileOperator
from app.crud.filter_utils.filters import FilterHandler
from app.crud.image_operation import ImageOperation
from app.crud.user_operation import UserOperation
from app.db import db_models
from app.schemes.models import cache_models, user_models, chat_models, document_models, partition_models, chunk_models, \
    file_models
from config import ServeConfig

# Admin Router
admin_router = APIRouter(prefix="/xiaoke_admin", tags=["后台管理员"])
admin_operator = AdminOperation(
    filter_handler=FilterHandler(
        db_model=db_models.User
    )
)
AdminCRUDRouter(
    router=admin_router,
    operator=admin_operator,
    response_model=user_models.ResponseAdmin,
    create_model=user_models.AdminCreate,
    update_model=user_models.AdminUpdate,
    keyword_search_model=user_models.AdminKeywordSearch,
)
file_router = APIRouter(prefix="/file", tags=["文件管理"])
file_operator = FileOperator(
    filter_handler=FilterHandler(
        db_model=db_models.File
    ),
    bucket_name=ServeConfig.minio_file_bucket_name
)

FileCRUDRouter(
    router=file_router,
    operator=file_operator,
    create_model=file_models.FileCreate,
    update_model=file_models.FileUpdate,
    response_model=file_models.ResponseFile,
    keyword_search_model=file_models.FileKeywordSearch,
    search_response_model=file_models.SearchFileResponse,
)

image_router = APIRouter(prefix="/public-images", tags=["图片管理"])
image_operator = ImageOperation(
    filter_handler=FilterHandler(
        db_model=db_models.Image
    ),
    bucket_name=ServeConfig.minio_public_images_bucket_name,
    public=True
)
ImageCRUDRouter(
    router=image_router,
    operator=image_operator,
    response_model=file_models.ResponseFile,
)

# Partition Router
partition_router = APIRouter(prefix="/partition", tags=["分区管理"])
partition_operator = BaseOperation(
    filter_handler=FilterHandler(
        db_model=db_models.Partition
    )
)

BaseCRUDRouter(
    router=partition_router,
    operator=partition_operator,
    response_model=partition_models.ResponsePartition,
    create_model=partition_models.PartitionCreate,
    update_model=partition_models.PartitionUpdate,
    keyword_search_model=partition_models.PartitionKeywordSearch,
    search_response_model=partition_models.SearchPartitionResponse,

)

# User Router
user_router = APIRouter(prefix="/user", tags=["用户管理"])
user_operator = UserOperation(
    filter_handler=FilterHandler(
        db_model=db_models.User
    )
)

UserCURouter(
    router=user_router,
    operator=user_operator,
    response_model=user_models.ResponseUser,
    create_model=user_models.UserCreate,
    update_model=user_models.UserUpdate
)

# Chunk Router
chunk_router = APIRouter(prefix="/chunk", tags=["Chunk Data Management"])
chunk_operator = ChunkOperation(
    filter_handler=FilterHandler(
        db_model=db_models.Chunk
    )
)
router = ChunkRouter(
    router=chunk_router,
    operator=chunk_operator,
    response_model=chunk_models.ResponseChunk,
    create_model=chunk_models.ChunkCreate,
    update_model=chunk_models.ChunkUpdate,
    keyword_search_model=chunk_models.ChunkKeywordSearch,
    search_response_model=chunk_models.SearchChunkResponse,
    vector_search_model=chunk_models.ChunkSearch,
    hybrid_search_model=chunk_models.HybridSearchModel,
)

# RAGCache Router
rag_cache_router = APIRouter(prefix="/rag_cache", tags=["RAGCache查询"])
rag_cache_operator = BaseOperation(
    filter_handler=FilterHandler(
        db_model=db_models.RAGCache
    )
)
CacheCRUDRouter(
    router=rag_cache_router,
    operator=rag_cache_operator,
    response_model=cache_models.ResponseRAGCache,
    create_model=cache_models.RAGCacheCreate,
    update_model=cache_models.RAGCacheUpdate,
    keyword_search_model=cache_models.RAGCacheKeywordSearch,
    search_response_model=cache_models.SearchRAGCacheResponse,

)

# Conversation Router
conversation_router = APIRouter(prefix="/conversation", tags=["会话查询"])
conversation_operator = BaseOperation(
    filter_handler=FilterHandler(
        db_model=db_models.Conversation
    )
)

BaseCRUDRouter(
    router=conversation_router,
    operator=conversation_operator,
    response_model=chat_models.ResponseConversation,
    create_model=chat_models.ConversationCreate,
    update_model=chat_models.ConversationUpdate,
    keyword_search_model=chat_models.ConversationKeywordSearch,
    search_response_model=chat_models.SearchConversationResponse,

)

# Response Record Router
response_record_router = APIRouter(prefix="/response_record", tags=["响应记录查询"])
response_record_operator = BaseOperation(
    filter_handler=FilterHandler(
        db_model=db_models.ResponseRecord
    )
)

BaseCRUDRouter(
    router=response_record_router,
    operator=response_record_operator,
    response_model=chat_models.ResponseResponseRecord,
    create_model=chat_models.ResponseRecordCreate,
    update_model=chat_models.ResponseRecordUpdate,
    keyword_search_model=chat_models.ResponseRecordKeywordSearch,
    search_response_model=chat_models.SearchResponseRecordResponse,
)

# Document Router
document_router = APIRouter(prefix="/document", tags=["文档查询"])
document_operator = BaseOperation(
    filter_handler=FilterHandler(
        db_model=db_models.Document
    )
)
BaseCRUDRouter(
    router=document_router,
    operator=document_operator,
    response_model=document_models.ResponseDocument,
    create_model=document_models.DocumentCreate,
    update_model=document_models.DocumentUpdate,
    keyword_search_model=document_models.DocumentKeywordSearch,
    search_response_model=document_models.SearchDocumentResponse,

)
