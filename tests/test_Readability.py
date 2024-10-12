import chardet
import requests
from readability import Document

# url = "https://www.nepu.edu.cn"
# url = "https://xsc.nepu.edu.cn/info/1287/3616.htm"
url = "https://baike.baidu.com/item/%E4%B8%9C%E5%8C%97%E7%9F%B3%E6%B2%B9%E5%A4%A7%E5%AD%A6/7434895"
response = requests.get(url)
detected_encoding = chardet.detect(response.content)['encoding']
response.encoding = response.apparent_encoding
html = response.text

doc = Document(html)
content = doc.summary()
import html2text
from urllib.parse import urlparse

base_url = urlparse(url).scheme + "://" + urlparse(url).netloc
md_content = html2text.html2text(content, baseurl=base_url)
print(md_content)
# print(content)
