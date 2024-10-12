from app.serves.prompts.base_prompt import base_prompt
from app.serves.prompts.base_prompt import check_query_complexity
from app.serves.prompts.base_prompt import E2C_translate
from app.serves.prompts.base_prompt import response_format_converter
from app.serves.prompts.base_prompt import query_decompose
from app.serves.prompts.base_prompt import keyword_extractor
from app.serves.prompts.base_prompt import retrieval_text_relevance
from app.serves.prompts.base_prompt import source_cite
from app.serves.prompts.base_prompt import multi_source_cite_merger
from app.serves.prompts.base_prompt import step_back_question
from app.serves.prompts.base_prompt import multi_step_back_question
from app.serves.prompts.base_prompt import rag_prompt


class PromptFactory:
    check_query_complexity = check_query_complexity.CheckQueryComplexity
    e2c_translate = E2C_translate.E2CTranslate
    response_format_convert = response_format_converter.ResponseFormatConverter
    query_decompose = query_decompose.QueryDecompose
    keyword_extractor = keyword_extractor.KeywordExtractor
    retrieval_text_relevance = retrieval_text_relevance.RetrievalTextRelevance
    source_cite_rag = source_cite.SourceCite
    multi_source_cite_merger = multi_source_cite_merger.MultiSourceCiteMerger
    step_back_query = step_back_question.StepBackQuestion
    multi_step_back_question = multi_step_back_question.MultiStepBackQuestion
    rag_prompt = rag_prompt.RAGPrompt
