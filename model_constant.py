from app.serves.model_serves.chat_model import ChatModel
from app.serves.model_serves.embedding_model import EmbeddingModel
from app.serves.model_serves.rag_model import RAGModel
from app.serves.model_serves.rerank_model import RerankModel

embedding_model: EmbeddingModel | None = None
chat_model: ChatModel | None = None
util_chat_model: ChatModel | None = None
rerank_model: RerankModel | None = None


def get_embedding_model():
    global embedding_model
    return embedding_model


def set_embedding_model(rag: RAGModel):
    global embedding_model
    embedding_model = rag


####

def get_chat_model():
    global chat_model
    return chat_model


def set_chat_model(rag: ChatModel):
    global chat_model
    chat_model = rag


####
def get_util_chat_model():
    global util_rag
    return util_rag


def set_util_chat_model(rag: ChatModel):
    global util_rag
    util_rag = rag


####

def get_rerank_model():
    global rerank_model
    return rerank_model


def set_rerank_model(rerank: RerankModel):
    global rerank_model
    rerank_model = rerank
