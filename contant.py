from app.serves.model_serves.rag_model import RAGModel

rag_embedding: RAGModel | None = None
rag_chat: RAGModel | None = None
util_rag: RAGModel | None = None


def get_rag_embedding():
    global rag_embedding
    return rag_embedding


def set_rag_embedding(rag: RAGModel):
    global rag_embedding
    rag_embedding = rag


def get_rag_chat():
    global rag_chat
    return rag_chat


def set_rag_chat(rag: RAGModel):
    global rag_chat
    rag_chat = rag


def get_util_rag():
    global util_rag
    return util_rag


def set_util_rag(rag: RAGModel):
    global util_rag
    util_rag = rag
