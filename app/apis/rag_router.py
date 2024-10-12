from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.apis.deps import get_db
from app.schemes.models.rag_serve_models import RAGServeModel, RAGResponse, RAGStreamResponse
from app.serves.model_serves.chat_model import ChatModel
from app.serves.model_serves.embedding_model import EmbeddingModel
from app.serves.model_serves.rerank_model import RerankModel
from app.serves.rag_service.rag_service import RAGService
from app.serves.rag_service.rag_stream_service import RAGStreamService
from app.serves.rag_service.rag_web_search import RAGWebSearch
from app.serves.rag_service.rag_web_search_stream_service import RAGStreamWebSearchService
from model_constant import get_embedding_model, get_chat_model, get_rerank_model
from fastapi.responses import StreamingResponse

rag_router = APIRouter(prefix="/rag_chat", tags=["RAG"])


@rag_router.post(path="/chat", response_model=RAGResponse)
async def rag_serve(model: RAGServeModel,
                    db: AsyncSession = Depends(get_db),
                    embedding_model: EmbeddingModel = Depends(get_embedding_model),
                    llm: ChatModel = Depends(get_chat_model)):
    rag_service = RAGService(db=db, embedding_model=embedding_model, llm=llm)
    response = await rag_service.generate_rag_response(model=model)
    return response


@rag_router.post(path="/stream-chat")
async def rag_stream_serve(model: RAGServeModel,
                           db: AsyncSession = Depends(get_db),
                           embedding_model: EmbeddingModel = Depends(get_embedding_model),
                           llm: ChatModel = Depends(get_chat_model)):
    rag_service = RAGStreamService(db=db, embedding_model=embedding_model, llm=llm)

    return StreamingResponse(rag_service.generate_rag_stream_response(model=model)
                             , media_type="text/event-stream")


@rag_router.post(path="/stream-chat-web_search", response_model=RAGStreamResponse)
async def rag_stream_web_search_serve(model: RAGServeModel,
                                      db: AsyncSession = Depends(get_db),
                                      embedding_model: EmbeddingModel = Depends(get_embedding_model),
                                      llm: ChatModel = Depends(get_chat_model),
                                      rerank_model: RerankModel = Depends(get_rerank_model)):
    rag_service = RAGWebSearch(db=db, embedding_model=embedding_model, llm=llm, rerank_model=rerank_model)
    return StreamingResponse(rag_service.generate_rag_web_search_response(model=model),
                             media_type="text/event-stream")
