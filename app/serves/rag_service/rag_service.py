import asyncio
import logging
import time

from llm_parse_json import parse_json
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.filter_utils.filters import FilterHandler
from app.crud.search_utils import hybrid_search
from app.db.db_models import Chunk
from app.schemes.models.chunk_models import HybridSearchModel
from app.schemes.models.rag_serve_models import RAGServeModel, RAGResponse
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


class RAGService:
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
            logging.info(f"LLM response received with total tokens: {self.total_tokens}")
            logging.debug(f"LLM response output: {result.output}")
            yield result.output

    async def generate_rag_stream_response(self,
                                           model: RAGServeModel,
                                           offset=0,
                                           max_depth=3):
        start_time = time.time()
        (user_question, limit, keyword_weight, vector_weight,
         recursive_query, use_vector_search, use_keyword_search,
         paragraph_number_ranking, filter_count) = (model.query, model.limit, model.keyword_weight, model.vector_weight,
                                                    model.recursive_query, model.use_vector_search,
                                                    model.use_keyword_search,
                                                    model.paragraph_number_ranking, model.filter_count)

        logging.info(f"Generating RAG response for question: {user_question}")
        json_complexity = await self.check_query_complexity(user_question)
        logging.debug(f"Query complexity: {json_complexity}")
        complexity = json_complexity["complexity"]

        json_queries = await self.handle_query_complexity(complexity, user_question)
        logging.debug(f"Queries: {json_queries}")

        responses = []
        retrieval_documents = []

        async def process_query(query):
            sub_documents = await self.get_hybrid_documents(self.db, query,
                                                            offset, limit, use_vector_search,
                                                            use_keyword_search, vector_weight,
                                                            keyword_weight, paragraph_number_ranking,
                                                            filter_count)
            logging.debug(f"Sub-documents length: {len(sub_documents)}")
            retrieval_documents.extend(sub_documents)
            if sub_documents:
                return await self.generate_response_from_documents(user_question=user_question,
                                                                   documents=sub_documents)
            elif recursive_query:
                return await self.handle_recursive_query(user_question, offset, limit,
                                                         vector_weight, keyword_weight,
                                                         max_depth, current_depth=1)
            return None

        tasks = [process_query(query) for query in json_queries]
        results = await asyncio.gather(*tasks)

        for result in results:
            if result:
                responses.append(result)

        if responses:
            if len(responses) > 1:
                final_response = await self.merge_responses(question=user_question,
                                                            responses=responses)
            else:
                final_response = responses[0]
        else:
            final_response = "Sorry, I can't find the answer to your question."

        end_time = time.time()
        elapsed_time = end_time - start_time

        logging.info("RAG response generation completed.")
        logging.info(f"Final response: {final_response}")

        return RAGResponse(response=final_response, retrieval_documents=retrieval_documents, time=elapsed_time)

    async def generate_rag_response(self,
                                    model: RAGServeModel,
                                    offset=0,
                                    max_depth=3) -> RAGResponse:
        start_time = time.time()
        (user_question, limit, keyword_weight, vector_weight,
         recursive_query, use_vector_search, use_keyword_search,
         paragraph_number_ranking, filter_count) = (model.query, model.limit, model.keyword_weight, model.vector_weight,
                                                    model.recursive_query, model.use_vector_search,
                                                    model.use_keyword_search,
                                                    model.paragraph_number_ranking, model.filter_count)

        logging.info(f"Generating RAG response for question: {user_question}")
        json_complexity = await self.check_query_complexity(user_question)
        logging.debug(f"Query complexity: {json_complexity}")
        complexity = json_complexity["complexity"]

        json_queries = await self.handle_query_complexity(complexity, user_question)
        logging.debug(f"Queries: {json_queries}")

        responses = []
        retrieval_documents = []

        async def process_query(query):
            sub_documents = await self.get_hybrid_documents(self.db, query,
                                                            offset, limit, use_vector_search,
                                                            use_keyword_search, vector_weight,
                                                            keyword_weight, paragraph_number_ranking,
                                                            filter_count)
            logging.debug(f"Sub-documents length: {len(sub_documents)}")
            retrieval_documents.extend(sub_documents)
            if sub_documents:
                return await self.generate_response_from_documents(user_question=user_question,
                                                                   documents=sub_documents)
            elif recursive_query:
                return await self.handle_recursive_query(user_question, offset, limit,
                                                         vector_weight, keyword_weight,
                                                         max_depth, current_depth=1)
            return None

        tasks = [process_query(query) for query in json_queries]
        results = await asyncio.gather(*tasks)

        for result in results:
            if result:
                responses.append(result)

        if responses:
            if len(responses) > 1:
                final_response = await self.merge_responses(question=user_question,
                                                            responses=responses)
            else:
                final_response = responses[0]
        else:
            final_response = "Sorry, I can't find the answer to your question."

        end_time = time.time()
        elapsed_time = end_time - start_time

        logging.info("RAG response generation completed.")
        logging.debug(f"Final response: {final_response}")

        return RAGResponse(response=final_response, retrieval_documents=retrieval_documents, time=elapsed_time)

    async def handle_recursive_query(self, user_question, offset, limit,
                                     vector_weight, keyword_weight,
                                     max_depth, current_depth=0):
        step_back_queries = []
        logging.info(f"Handling recursive query at depth {current_depth} for question: {user_question}")
        if current_depth >= max_depth:
            logging.info("Max depth reached for recursive query.")
            return None

        step_back_query = await self.generate_multi_step_back_question(user_question, step_back_queries)
        logging.debug(f"Step-back query: {step_back_query}")
        if step_back_query:
            sub_documents = await self.get_hybrid_documents(self.db,
                                                            step_back_query,
                                                            offset, limit,
                                                            vector_weight,
                                                            keyword_weight)
            step_back_queries.append(step_back_query)

            # sub_documents = await self.judge_documents_relevance(user_question=user_question,
            #                                                      documents=sub_documents)
            logging.debug(f"Sub-documents for recursive query length : {len(sub_documents)}")
            if sub_documents:
                response = await self.generate_response_from_documents(user_question, sub_documents)
                return response
        return None

    async def handle_query_complexity(self, complexity, user_question):
        logging.info(f"Handling query complexity: {complexity}")
        if complexity:
            return await self.query_decompose(user_question)
        return [user_question]

    async def merge_responses(self, question, responses):
        logging.info("Merging responses.")
        logging.debug(f"Responses to merge: {responses}")
        merger_prompt = PromptFactory.multi_source_cite_merger(question=question,
                                                               responses=responses)
        return await self.get_llm_response(merger_prompt.to_messages())

    async def generate_response_from_documents(self, user_question, documents):
        logging.info(f"Generating response from documents for question: {user_question}")
        logging.debug(f"Documents: {documents}")
        source_cite_rag_prompt = PromptFactory.source_cite_rag(question=user_question, documents=documents)
        return await self.get_llm_response(source_cite_rag_prompt.to_messages())

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
        return [result.page_content for result in hybrid_search_results]

    async def judge_document_relevance(self, user_question, document):
        logging.info(f"Judging relevance of document for question: {user_question}")
        judge_relevance_prompt = PromptFactory.retrieval_text_relevance(user_question=user_question, document=document)
        relevance = await self.get_llm_response(judge_relevance_prompt.to_messages())
        json_relevance = await self.response_convert_to_json(relevance, output_format="""{"relevance": true/false}""")
        logging.debug(f"Document relevance: {json_relevance}")
        return json_relevance

    async def judge_documents_relevance(self, user_question, documents) -> list:
        relevant_documents = []
        for document in documents:
            relevance = await self.judge_document_relevance(user_question, document)
            if relevance.get("relevance"):
                relevant_documents.append(document)
            else:
                self.irrelevant_documents.add(document)
        return relevant_documents

    async def check_query_complexity(self, user_question: str) -> dict:
        logging.info(f"Checking query complexity for question: {user_question}")
        complexity_prompt = PromptFactory.check_query_complexity(user_question, output_format="0/1")
        complexity = await self.get_llm_response(complexity_prompt.to_messages())
        logging.debug(f"Complexity: {complexity}")
        json_format_response = await self.response_convert_to_json(complexity, output_format="""
        {
        "complexity": true/false
        }
        """)
        logging.debug(f"Complexity JSON response: {json_format_response}")
        return json_format_response

    async def query_decompose(self, query: str):
        logging.info(f"Decomposing query: {query}")
        query_decompose_prompt = PromptFactory.query_decompose(query)
        query_decompose_result = await self.get_llm_response(query_decompose_prompt.to_messages())
        json_queries = await self.response_convert_to_json(query_decompose_result,
                                                           output_format="""[query1, query2,……]""")
        logging.debug(f"Decomposed queries: {json_queries}")
        return parse_llm_output(json_queries)

    async def response_convert_to_json(self, response: str, output_format: str) -> dict | list:
        logging.info("Converting response to JSON.")
        json_format_prompt = PromptFactory.response_format_convert(response, output_format=output_format)
        json_format_response = await self.get_llm_response(json_format_prompt.to_messages())
        logging.debug(f"JSON format response: {json_format_response}")
        return parse_llm_output(json_format_response)

    async def generate_multi_step_back_question(self, input_text, rewritten_records: list):
        logging.info(f"Generating multi-step back question for input: {input_text}")
        multi_step_back_query_prompt = PromptFactory.multi_step_back_question(input_text=input_text,
                                                                              rewritten_records=rewritten_records)
        return await self.get_llm_response(multi_step_back_query_prompt.to_messages())

    async def e2c_translate(self, text: str) -> str:
        logging.info(f"Translating text from English to Chinese: {text}")
        e2c_translate = PromptFactory.e2c_translate(text)
        return await self.get_llm_response(e2c_translate.to_messages())

    async def llm_query2keywords(self, query: str, keyword_count: int = 3) -> list:
        logging.info(f"Extracting keywords from query: {query}")
        keyword_extract_prompt = PromptFactory.keyword_extractor(query)
        keywords = await self.get_llm_response(keyword_extract_prompt.to_messages(keyword_count=keyword_count))
        json_keywords = await self.response_convert_to_json(keywords, output_format="""[keyword1, keyword2,……]""")
        logging.debug(f"Extracted keywords: {json_keywords}")
        return json_keywords
