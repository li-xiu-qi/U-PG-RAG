from boilerpy3 import extractors
from requests import get

# url = "https://www.nepu.edu.cn"
# url = "https://xsc.nepu.edu.cn/info/1287/3616.htm"
url = "https://baike.baidu.com/item/%E4%B8%9C%E5%8C%97%E7%9F%B3%E6%B2%B9%E5%A4%A7%E5%AD%A6/7434895"
response = get(url)
response.encoding = response.apparent_encoding
html = response.text

extractor = extractors.NumWordsRulesExtractor()  # 内容比较全，有点像是去掉了导航的多余内容，但是他对于表格的处理不是很好
# extractor = extractors.ArticleExtractor() # 少了很多内容
# extractor = extractors.CanolaExtractor() # 也是少了很多内容，但是比ArticleExtractor多，效果也更好，但是无法处理表格
# extractor = extractors.DefaultExtractor() # 也是少了很多内容，但是比CanolaExtractor多，效果由于无法处理表格导致看起来不太好
# extractor = extractors.KeepEverythingExtractor() # 保留了所有内容，包括导航等
# extractor = extractors.LargestContentExtractor() # 内容很少，比ArticleExtractor还少，但是效果也不好

content = extractor.get_content(html)

print(content)
