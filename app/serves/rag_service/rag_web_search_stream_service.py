import logging
import time
from urllib.parse import urlparse, urlunparse
from htmldate import find_date
from llm_parse_json import parse_json
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.filter_utils.filters import FilterHandler
from app.crud.search_utils import hybrid_search
from app.db.db_models import Chunk
from app.schemes.models.chunk_models import HybridSearchModel
from app.schemes.models.rag_serve_models import RAGServeModel, RAGStreamResponse
from app.serves.file_processing.md_spliter import MarkdownSpliter
from app.serves.model_serves.chat_model import ChatModel
from app.serves.model_serves.embedding_model import EmbeddingModel
from app.serves.model_serves.mmr import MemoryVectorSearch
from app.serves.model_serves.types import LLMInput, Message, EmbeddingInput
from app.serves.prompts.base_prompt import PromptFactory
from app.serves.rag_service.utils import query2keywords
from app.serves.web2md.index import Web2md
from app.serves.web_search import SiteFilter, SearchResult, SearchFactory
from config import ServeConfig
from requests import post

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


class RAGStreamWebSearchService:
    def __init__(self, db: AsyncSession, embedding_model: EmbeddingModel, llm: ChatModel):
        self.embedding_model = embedding_model
        self.llm = llm
        self.embedding_model_name = ServeConfig.embedding_model_name
        self.model_name = ServeConfig.model_name
        # self.model_name = "Vendor-A/Qwen/Qwen2-72B-Instruct"
        self.total_tokens = 0
        self.db = db
        self.irrelevant_documents = set()
        self.site_filter = SiteFilter(cache_dir=ServeConfig.site_filter_path)
        self.memory_vector_store = MemoryVectorSearch(model_name=self.embedding_model_name,
                                                      embedding_model=self.embedding_model,
                                                      use_index=True)

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
            logging.debug(f"LLM response output: {result.output}")
            yield result.output

    async def generate_rag_stream_web_search_response(self, model: RAGServeModel):
        start_time = time.time()
        (user_question, limit, keyword_weight, vector_weight,
         recursive_query, use_vector_search, use_keyword_search,
         paragraph_number_ranking, filter_count) = (model.query, model.limit, model.keyword_weight, model.vector_weight,
                                                    model.recursive_query, model.use_vector_search,
                                                    model.use_keyword_search,
                                                    model.paragraph_number_ranking, model.filter_count)
        # TODO: 敏感问题拒绝
        web2md_remove_links = Web2md(remove_links=True)
        web2md = Web2md(remove_links=False)
        # max_results = 30
        # keywords = await query2keywords(user_question, keyword_count=-1)
        # keyword = " ".join(keywords)
        # # TODO 后续填加site映射
        # # keyword_query = f"{keyword} site:{site}"
        # keyword_query = f"{keyword}"
        # web_search = SearchFactory(engine_type=ServeConfig.search_engine)
        # search_results = web_search.search(query=user_question, max_results=max_results)
        ######
        from .nepu import web_search_result
        search_results = [SearchResult(title=result["title"],
                                       url=result["href"],
                                       description=result["body"],
                                       ) for result in web_search_result[:20]]
        ######
        embedding_documents = []
        valid_search_results = []
        time_logs = []

        for result in search_results:
            if self.site_filter.check_url(result.url):
                continue
            valid_search_results.append(result)

        v_results_start_time = time.time()
        for v_result in valid_search_results:
            v_result_start_time = time.time()
            fetcher_html_start_time = time.time()
            html_content = self.html_fetcher.fetch_html(url=v_result.url)
            fetcher_html_end_time = time.time()
            time_logs.append(f"Time taken to fetch html: {fetcher_html_end_time - fetcher_html_start_time}")
            if not html_content:
                logger.info(f"Failed to fetch URL: {v_result.url}")
                self.site_filter.add_url(v_result.url)
                continue
            date = find_date(html_content)
            parsed_url = urlparse(v_result.url)
            favicon_url = urlunparse((parsed_url.scheme, parsed_url.netloc, '/favicon.ico', '', '', ''))
            html2md_start_time = time.time()
            web2md_remove_links_result = web2md_remove_links.html2md(html_content=html_content)
            html2md_end_time = time.time()
            time_logs.append(f"Time taken to convert html to markdown: {html2md_end_time - html2md_start_time}")
            logger.info(f"Fetched URL: {v_result.url}")
            result_length = len(web2md_remove_links_result)
            logger.info(f"Result length: {result_length}")
            embedding_documents.append(web2md_remove_links_result)
            ####

            md_spliter = MarkdownSpliter()
            md_chunks_start_time = time.time()
            md_chunks = await md_spliter.nested_split_markdown(text=web2md_remove_links_result)
            md_chunks_end_time = time.time()
            time_logs.append(f"Time taken to split markdown: {md_chunks_end_time - md_chunks_start_time}")
            v_result.date = date
            v_result.favicon = favicon_url
            metadata = md_chunks[0].metadata.update({
                "date": date,
                "favicon": favicon_url,
                "all_links": md_spliter.all_links
            })
            index_start_time = time.time()
            await self.memory_vector_store.add_documents(documents=[chunk.content for chunk in md_chunks],
                                                         metadata=metadata)
            index_end_time = time.time()
            time_logs.append(f"Time taken to index: {index_end_time - index_start_time}")
            yield f"data: {RAGStreamResponse(data_type='web_search', result=v_result).model_dump_json()}\n\n"
            web2md_start_time = time.time()
            web2md_result, link_resource = web2md.html2md(html_content, current_url=v_result.url)
            web2md_end_time = time.time()
            time_logs.append(
                f"Time taken to convert html to markdown with links: {web2md_end_time - web2md_start_time}")
            yield f"data: {RAGStreamResponse(data_type='link_resource', result=link_resource).model_dump_json()}\n\n"
            v_result_end_time = time.time()
            time_logs.append(f"Time taken to process valid search result: {v_result_end_time - v_result_start_time}")
        v_results_end_time = time.time()
        time_logs.append(f"Time taken to process vali`d search results: {v_results_end_time - v_results_start_time}")
        mmr_start_time = time.time()
        documents = await self.memory_vector_store.mmr(query=user_question, top_k=limit)
        mmr_end_time = time.time()
        time_logs.append(f"Time taken to perform MMR: {mmr_end_time - mmr_start_time}")
        response = ""
        async for res in self.generate_stream_response_from_documents(user_question,
                                                                      [doc.content for doc in documents]):
            response += res
            yield f"data: {RAGStreamResponse(data_type='assistant', result=res).model_dump_json()}\n\n"
        logger.info(f"本次response：{response}")

        for log in time_logs:
            logging.info(log)
        end_time = time.time()
        logging.info(f"Total time taken for generate_rag_stream_web_search_response: {end_time - start_time}")

    async def generate_stream_response_from_documents(self, user_question, documents):
        logging.info(f"Generating response from documents for question: {user_question}")
        context = ""
        for i, doc in enumerate(documents):
            context += f"Document {i + 1}: {doc}\n"
        with open("test.md", "w") as f:
            f.write(context)
        print(f"context length: {len(context)}")
        source_cite_rag_prompt = PromptFactory.rag_prompt(text=user_question, context=context)
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
        keywords = await query2keywords(query, keyword_count=-1)
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
