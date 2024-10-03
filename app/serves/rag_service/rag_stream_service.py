"""
use example:
result = requests.post(stream_url, json=data, stream=True)
buffer = ""
for line in result.iter_lines():
    if line:
        decoded_line = line.decode("utf-8").strip("data: \n")
        buffer += decoded_line
        try:
            json_data = json.loads(buffer)

            json_data_str = json.dumps(json_data, indent=2, ensure_ascii=False)
            # print(json_data.get("data_type"))
            if json_data.get("data_type") == "answer":
                print(json_data.get("result"), end="")
            buffer = ""
        except json.JSONDecodeError:
            # Incomplete JSON, continue accumulating
            continue
"""

import logging
from llm_parse_json import parse_json
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.filter_utils.filters import FilterHandler
from app.crud.search_utils import hybrid_search
from app.db.db_models import Chunk
from app.schemes.models.chunk_models import HybridSearchModel
from app.schemes.models.rag_serve_models import RAGServeModel, RAGStreamResponse
from app.serves.model_serves.chat_model import ChatModel
from app.serves.model_serves.embedding_model import EmbeddingModel
from app.serves.model_serves.types import LLMInput, Message, EmbeddingInput
from app.serves.prompts.base_prompt import PromptFactory
from app.serves.rag_service.utils import query2keywords

logger = logging.getLogger(__name__)


def parse_llm_output(data):
    try:
        response = parse_json(data)
        return response
    except Exception as e:
        logging.error(f"Error parsing LLM output: {e}")
        split_symbol = "___" * 10
        logging.error(f"Data:\n{split_symbol}\n {data}\n{split_symbol}")
        return None


class RAGStreamService:
    def __init__(self, db: AsyncSession, embedding_model: EmbeddingModel, llm: ChatModel):
        self.embedding_model = embedding_model
        self.llm = llm
        self.model_name = "Qwen/Qwen2.5-7B-Instruct"
        # self.model_name = "Vendor-A/Qwen/Qwen2-72B-Instruct"
        self.total_tokens = 0
        self.db = db
        self.irrelevant_documents = set()
        logging.info("RAGService initialized.")

    async def get_llm_response(self, messages: list[dict]):
        logging.info("Getting LLM response.")
        logging.debug(f"Messages: {messages}")
        messages = [Message(**mes) for mes in messages]
        input_content = LLMInput(name=self.model_name, input_content=messages)
        response = await self.llm.chat(model_input=input_content)
        self.total_tokens += response.total_tokens
        logging.info(f"LLM response received with total tokens: {self.total_tokens}")
        logging.debug(f"LLM response output: {response.output}")
        return response.output

    async def get_llm_stream_response(self, messages: list[dict]):
        logging.info("Getting LLM stream response.")
        logging.debug(f"Messages: {messages}")
        messages = [Message(**mes) for mes in messages]
        input_content = LLMInput(name=self.model_name, input_content=messages)
        results = self.llm.stream_chat(model_input=input_content)
        async for result in results:
            self.total_tokens += result.total_tokens
            if self.total_tokens != 0:
                logging.info(f"LLM response received with total tokens: {self.total_tokens}")
            logging.info(f"LLM response output: {result.output}")
            yield result.output

    async def generate_rag_stream_response(self,
                                           model: RAGServeModel,
                                           offset=0):
        (user_question, limit, keyword_weight, vector_weight,
         recursive_query, use_vector_search, use_keyword_search,
         paragraph_number_ranking, filter_count) = (model.query, model.limit, model.keyword_weight, model.vector_weight,
                                                    model.recursive_query, model.use_vector_search,
                                                    model.use_keyword_search,
                                                    model.paragraph_number_ranking, model.filter_count)

        documents = await self.get_hybrid_documents(db=self.db, query=user_question,
                                                    offset=offset, limit=limit,
                                                    use_vector_search=use_vector_search,
                                                    use_keyword_search=use_keyword_search,
                                                    vector_weight=vector_weight,
                                                    keyword_weight=keyword_weight,
                                                    paragraph_number_ranking=paragraph_number_ranking,
                                                    filter_count=filter_count
                                                    )
        yield f"data: {RAGStreamResponse(data_type='document', result=documents).model_dump_json()}\n\n"
        async for res in self.generate_stream_response_from_documents(user_question,
                                                                      [doc["page_content"] for doc in documents]):
            yield f"data: {RAGStreamResponse(data_type='answer', result=res).model_dump_json()}\n\n"

    async def generate_stream_response_from_documents(self, user_question, documents):
        logging.info(f"Generating response from documents for question: {user_question}")
        source_cite_rag_prompt = PromptFactory.source_cite_rag(question=user_question, documents=documents)
        async for res in self.get_llm_stream_response(source_cite_rag_prompt.to_messages()):
            yield res

    async def get_hybrid_documents(self, db, query: str,
                                   offset=0, limit=20,
                                   use_vector_search=True,
                                   use_keyword_search=True,
                                   vector_weight=1.0,
                                   keyword_weight=1.0,
                                   paragraph_number_ranking=False,
                                   filter_count=-1) -> list:
        logging.info(f"Performing hybrid search for query: {query}")
        keywords = await query2keywords(query, keyword_count=2)
        logging.debug(f"Keywords: {keywords}")
        model = HybridSearchModel(page_content=query, keywords=keywords,
                                  offset=offset, limit=limit,
                                  use_vector_search=use_vector_search,
                                  use_keyword_search=use_keyword_search,
                                  vector_weight=vector_weight,
                                  keyword_weight=keyword_weight,
                                  paragraph_number_ranking=paragraph_number_ranking,
                                  filter_count=filter_count)
        if model.vector is None and model.page_content:
            model_input = EmbeddingInput(input_content=[model.page_content])
            embedding_output = await self.embedding_model.embedding(model_input=model_input)
            model.vector = embedding_output.output[0]
        hybrid_search_results = await hybrid_search(db, model, FilterHandler(db_model=Chunk))
        logging.debug(f"Hybrid search results: {hybrid_search_results}")
        return [{"page_content": result.page_content, "doc_metadata": result.doc_metadata} for result in
                hybrid_search_results]
