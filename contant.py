from app.serves.model_serves.rag_model import RAGModel

rag_embedding: RAGModel | None = None
rag_chat: RAGModel | None = None


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
