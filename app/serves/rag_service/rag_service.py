from app.serves.model_serves.rag_model import RAGModel


class RAGService:
    def __init__(self, embedding_model: RAGModel, llm: RAGModel):
        self.embedding_model = embedding_model
        self.llm = llm

    def generate_response(self, user_question: str):
        pass
