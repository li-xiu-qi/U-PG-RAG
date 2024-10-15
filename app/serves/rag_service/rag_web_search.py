import copy
import logging
from typing import List
from urllib.parse import urlparse

import diskcache
from html2text import html2text
from llm_parse_json import parse_json
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemes.models.rag_serve_models import RAGServeModel, RAGStreamResponse
from app.serves.fetch_web_resouece.fetch_web_resource import HTMLFetcher, ZhiPuWebSearch
from app.serves.file_processing.line_paragraph_filter import LineParagraphFilter
from app.serves.file_processing.split import MarkdownTextRefSplitter, MarkdownHeaderTextSplitter
from app.serves.file_processing.tokenizer_filter import TokenizerFilter
from app.serves.model_serves.chat_model import ChatModel
from app.serves.model_serves.embedding_model import EmbeddingModel
from app.serves.model_serves.mmr import MemoryVectorSearch
from app.serves.model_serves.rerank_model import RerankModel
from app.serves.model_serves.types import LLMInput, Message
from app.serves.prompts.base_prompt import PromptFactory
from app.serves.rag_service.utils import to_keywords
from app.serves.web_search import SiteFilter
from config import ServeConfig
from readability import Document

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


class URL(BaseModel):
    link: str | None = ""
    title: str | None = ""


class UrlResource(BaseModel):
    image_urls: List[str]
    file_urls: List[str]


class SearchResult(BaseModel):
    url: str | None = ""
    favicon: str | None = ""
    title: str | None = ""
    description: str | None = ""
    media: str | None = ""
    html_content: str | None = ""
    publish_date: str | None = ""
    url_resource: UrlResource | None = None


class RAGWebSearch:
    def __init__(self, db: AsyncSession,
                 embedding_model: EmbeddingModel,
                 llm: ChatModel,
                 rerank_model: RerankModel):
        self.embedding_model = embedding_model
        self.llm = llm
        self.embedding_model_name = ServeConfig.embedding_model_name
        self.model_name = ServeConfig.model_name
        self.total_tokens = 0
        self.db = db
        self.irrelevant_documents = set()
        self.site_filter = SiteFilter(cache_dir=ServeConfig.site_filter_path)
        self.memory_vector_store = MemoryVectorSearch(model_name=self.embedding_model_name,
                                                      embedding_model=self.embedding_model,
                                                      use_index=True)
        self.filter = LineParagraphFilter()
        self.rerank_model = rerank_model

        logging.info("RAGService initialized.")

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

    async def generate_rag_web_search_response(self, model: RAGServeModel):
        (user_question, limit, keyword_weight, vector_weight,
         recursive_query, use_vector_search, use_keyword_search,
         paragraph_number_ranking, filter_count) = (model.query, model.limit, model.keyword_weight, model.vector_weight,
                                                    model.recursive_query, model.use_vector_search,
                                                    model.use_keyword_search,
                                                    model.paragraph_number_ranking, model.filter_count)
        # ##
        # yield f"data: {RAGStreamResponse(data_type='web_search_start', result='Web search started.').model_dump_json()}\n\n"
        # ##
        school_site = model.school_site
        search_engine = ZhiPuWebSearch(api_key=ServeConfig.zhipu_api_configs[0]["api_key"])
        keywords = to_keywords(user_question)
        keyword = " ".join(keywords)
        print(f"Keyword: {keyword}")
        results = search_engine.search(keyword, school_site)

        cache = diskcache.Cache('./html_cache')
        fetcher = HTMLFetcher(cache=cache)

        enriched_results = fetcher.fetch_html_batch(results, timeout=5)
        documents = []
        async for search_result in enriched_results:
            data = copy.deepcopy(search_result)
            data.html_content = ""
            yield f"data: {RAGStreamResponse(data_type='web_search', result=data).model_dump_json()}\n\n"
            url = search_result.url
            base_url = urlparse(url).scheme + "://" + urlparse(url).netloc
            doc = Document(search_result.html_content)
            html_content = doc.summary()
            md_content = html2text(html_content, baseurl=base_url)
            chunks = MarkdownHeaderTextSplitter().create_chunks(text=md_content)
            documents.extend([chunk.content for chunk in chunks])
        # ##
        # yield f"data: {RAGStreamResponse(data_type='data_process', result=documents).model_dump_json()}\n\n"
        # ##

        docs = self.filter.filter_similar_documents(documents=[chunk for chunk in documents],
                                                    threshold=0.75)
        valid_contents = await self.rerank_model.get_sorted_documents(query=user_question, documents=docs)
        with open("test.md", "w") as f:
            f.write("\n".join([doc for doc in docs]))
        print(f"Docs_length: {len(docs)}")
        async for res in self.generate_stream_response_from_documents(user_question, [doc for doc in valid_contents]):
            yield f"data: {RAGStreamResponse(data_type='assistant', result=res).model_dump_json()}\n\n"

    async def generate_stream_response_from_documents(self, user_question, documents):
        logging.info(f"Generating response from documents for question: {user_question}")
        context = ""
        for i, doc in enumerate(documents):
            context += (f"Document {i + 1}: {doc}"
                        f"___"
                        f"\n")
        with open("test.md", "w") as f:
            f.write(context)
        print(f"context length: {len(context)}")
        source_cite_rag_prompt = PromptFactory.rag_prompt(text=user_question, context=context)
        async for res in self.get_llm_stream_response(source_cite_rag_prompt.to_messages()):
            yield res
