from llm_parse_json import parse_json
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.filter_utils.filters import FilterHandler
from app.crud.search_utils import hybrid_search
from app.db.db_models import Chunk
from app.schemes.models.chunk_models import HybridSearchModel
from app.serves.model_serves.rag_model import RAGModel
from app.serves.model_serves.types import LLMInput, Message
from app.serves.prompts.base_prompt import PromptFactory
from app.serves.rag_service.utils import query2keywords


def parse_llm_output(data):
    try:
        response = parse_json(data)
        return response
    except Exception as e:
        print(e)
        return None


class RAGService:
    def __init__(self, db: AsyncSession, embedding_model: RAGModel, llm: RAGModel):
        self.embedding_model = embedding_model
        self.llm = llm
        self.model_name = ""
        self.total_tokens = 0
        self.db = db

    async def get_llm_response(self, messages: list[dict]):
        messages = [Message(**mes) for mes in messages]
        input_content = LLMInput(name=self.model_name, input_content=messages)
        response = await  self.llm.chat(input_content)
        self.total_tokens += response.total_tokens
        return response.output

    async def generate_response(self, user_question: str,
                                recursive_query: bool = False,
                                offset=0,
                                limit=20,
                                keyword_weight=1.0,
                                vector_weight=1.0,
                                max_depth=3
                                ):
        # TODO keyi
        # TODO 检查输入的问题是否符合规范
        # 当前版本默认是能正常解析每次的json数据
        # TODO json解析错误处理
        # 默认输入的是一个问题
        # TODO 检查是否是问题

        # 检查问题的复杂性
        json_complexity = await self.check_query_complexity(user_question)
        complexity = json_complexity["complexity"]

        json_queries = []
        if complexity == 1:
            # 复杂问题
            # 先将问题分解成多个子问题
            json_queries = await self.query_decompose(user_question)
        elif complexity == 0:
            # 简单问题
            json_queries = [user_question]
            # TODO complexity 有可能会出错，先做个标记，默认不会出错
        # 遍历子问题
        responses = []
        documents = []
        for query in json_queries:
            # TODO 多个问题可以并行处理
            # 外部的responses 用来存储每个子问题的sub_responses
            # 外部的documents 用来存储每个子问题的sub_documents
            sub_documents = []
            # 混合检索
            retrieval_documents = await self.get_hybrid_document(db=self.db,
                                                                 query=query,
                                                                 offset=offset,
                                                                 limit=limit,
                                                                 vector_weight=vector_weight,
                                                                 keyword_weight=keyword_weight,
                                                                 )
            # retrieval_documents 的内容不要与documents重复了，过滤下
            retrieval_documents = [document for document in retrieval_documents if document not in documents]

            if retrieval_documents:
                # 判断文档相关性
                for document in retrieval_documents:
                    json_relevance = await self.judge_document_relevance(user_question, document)
                    relevance = json_relevance["relevance"]
                    if relevance == 1:
                        sub_documents.append(document)

            if sub_documents:
                response = await self.generate_response_from_documents(user_question, sub_documents)
                responses.append(response)
            else:
                # 如果documents为空，说明没有找到相关文档 TODO 此处应该继续递归重新修改问题，继续查询，暂时不做处理
                # 开始做递归查询，先使用后退提示的方式修改问题，然后重新查询，我们设置一个最大深度，防止无限递归，还有设置一个是否递归查询的标志
                # 问题改写
                rewritten_records = []
                current_depth = 0
                if recursive_query and current_depth < max_depth:
                    current_depth += 1
                    step_back_query = await self.generate_multi_step_back_question(user_question, rewritten_records)
                    # 重新查询
                    if step_back_query:
                        sub_documents = await self.get_hybrid_document(self.db,
                                                                       step_back_query,
                                                                       offset=offset,
                                                                       limit=limit,
                                                                       vector_weight=vector_weight,
                                                                       keyword_weight=keyword_weight)
                        # 过滤下
                        sub_documents = [document for document in sub_documents if document not in documents]
                        if sub_documents:
                            response = await self.generate_response_from_documents(user_question, sub_documents)
                            responses.append(response)
                    else:
                        pass
                        # responses.append("Sorry, I can't find the answer to your question.")
                else:
                    pass
                    # responses.append("Sorry, I can't find the answer to your question.")
                # await self.get_hybrid_document(db=self.db, query=query)
        # 将responses合并
        if responses:
            merged_response = await self.merge_responses(responses)
            return merged_response
        else:
            return "Sorry, I can't find the answer to your question."

    async def merge_responses(self, responses):
        merger_prompt = PromptFactory.multi_source_cite_merger(responses)
        merged_response = await self.get_llm_response(merger_prompt.to_messages())
        return merged_response

    async def get_step_back_query(self, user_question):
        # 递归查询
        step_back_query_prompt = PromptFactory.step_back_query(user_question)
        step_back_query = await self.get_llm_response(step_back_query_prompt.to_messages())
        return step_back_query

    async def generate_multi_step_back_question(self, input_text, rewritten_records: list):
        # 生成后退提示问题
        multi_step_back_query_prompt = PromptFactory.multi_step_back_question(input_text=input_text,
                                                                              rewritten_records=rewritten_records)
        multi_step_back_query = await self.get_llm_response(multi_step_back_query_prompt.to_messages())
        return multi_step_back_query

    async def generate_response_from_documents(self, user_question, documents):
        # 生成回复
        source_cite_rag_prompt = PromptFactory.source_cite_rag(user_question=user_question,
                                                               documents=documents)
        response = await self.get_llm_response(source_cite_rag_prompt.to_messages())
        return response

    # 混合检索
    async def get_hybrid_document(self, db,
                                  query: str,
                                  offset=0,
                                  limit=20,
                                  vector_weight=1.0,
                                  keyword_weight=1.0) -> list:
        keywords = await query2keywords(query, keyword_count=2)
        model = HybridSearchModel(page_content=query,
                                  keywords=keywords,
                                  offset=offset,
                                  limit=limit,
                                  vector_weight=vector_weight,
                                  keyword_weight=keyword_weight)
        documents = await hybrid_search(db, model, FilterHandler(db_model=Chunk))
        return documents

    # 判断文档相关性
    async def judge_document_relevance(self, user_question, document):
        judge_relevance_prompt = PromptFactory.retrieval_text_relevance(
            user_question=user_question,
            document=document,
        )
        relevance = await self.get_llm_response(judge_relevance_prompt.to_messages())
        json_relevance = await self.response_convert_to_json(relevance, output_format="""{"relevance": 0/1}""")
        return json_relevance

    async def check_query_complexity(self, user_question: str) -> dict:
        """
        检查问题的复杂性
        :param user_question:
        :return: {"complexity": 0/1}
        """
        complexity_prompt = PromptFactory.check_query_complexity(user_question,
                                                                 output_format="0/1")
        complexity = await  self.get_llm_response(complexity_prompt.to_messages())
        json_format_response = await self.response_convert_to_json(complexity, output_format="""
        {
        "complexity": 0/1
        }
        """)
        return json_format_response

    async def query_decompose(self, query: str):
        """
        将问题分解成多个子问题
        :param query:
        :return: [query1, query2,……]
        """
        query_decompose_prompt = PromptFactory.query_decompose(query)
        query_decompose_result = await self.get_llm_response(query_decompose_prompt.to_messages())
        json_queries = await self.response_convert_to_json(query_decompose_result,
                                                           output_format="""[query1, query2,……]""")
        return parse_llm_output(json_queries)

    async def response_convert_to_json(self, response: str, output_format: str) -> dict | list:
        json_format_prompt = PromptFactory.response_format_convert(response,
                                                                   output_format=output_format)
        json_format_response = await self.get_llm_response(json_format_prompt.to_messages())

        return parse_llm_output(json_format_response)

    async def e2c_translate(self, text: str) -> str:
        """
        英文转中文
        :param text:str
        :return: str
        """
        e2c_translate = PromptFactory.e2c_translate(text)
        return await self.get_llm_response(e2c_translate.to_messages())
