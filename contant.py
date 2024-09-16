from app.serves.model_serves import RAG

# 全局变量定义

rag_embedding: RAG | None = None
rag_chat: RAG | None = None


def get_rag_embedding():
    global rag_embedding
    return rag_embedding


def set_rag_embedding(rag: RAG):
    global rag_embedding
    rag_embedding = rag


def get_rag_chat():
    global rag_chat
    return rag_chat


def set_rag_chat(rag: RAG):
    global rag_chat
    rag_chat = rag
