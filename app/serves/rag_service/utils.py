import jieba.analyse


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
    json_keywords = jieba.analyse.extract_tags(query, topK=keyword_count, withWeight=True,
                                               allowPOS=('n', 'nr', 'ns', 'nt', 'nz'))
    return json_keywords
