import jieba
import jieba.analyse
from nltk.corpus import stopwords


async def query2keywords(query: str, keyword_count: int = 3) -> list:
    # keyword_extract_prompt = PromptFactory.keyword_extractor(query)
    # keywords = await self.get_llm_response(keyword_extract_prompt.to_messages(keyword_count=keyword_count))
    # json_keywords = await self.response_convert_to_json(keywords, output_format="""[keyword1, keyword2,……]""")
    # 使用jieba 分词
    """
    n：名词
    nr：人名
    ns：地名
    nt：机构团体名
    nz：其他专有名词
    v：动词
    a：形容词
    d：副词
    m：数词
    q：量词
    r：代词
    p：介词
    c：连词
    u：助词
    xc：其他虚词

    """
    keywords = jieba.analyse.extract_tags(query, topK=keyword_count, withWeight=True,
                                          allowPOS=('n', 'nr', 'ns', 'nt', 'nz'))
    json_keywords = [keyword[0] for keyword in keywords]
    return json_keywords


def to_keywords(input_string, num_keywords=-1):
    """将句子转成检索关键词序列，并选择最长的几个词"""
    # 按搜索引擎模式分词
    word_tokens = jieba.cut_for_search(input_string)

    # 加载停用词表
    stop_words = set(stopwords.words('chinese'))

    # 去除停用词
    filtered_sentence = [w for w in word_tokens if w not in stop_words]

    # 按照词的长度排序
    sorted_keywords = sorted(filtered_sentence, key=len, reverse=True)

    # 选择最长的几个词
    top_keywords = sorted_keywords[:num_keywords]

    return ' '.join(top_keywords)


