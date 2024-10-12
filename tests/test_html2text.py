from urllib.parse import urlparse

from html2text import html2text
from requests import get

# url = "https://www.nepu.edu.cn"
# url = "https://xsc.nepu.edu.cn/info/1287/3616.htm"
url = "https://baike.baidu.com/item/%E4%B8%9C%E5%8C%97%E7%9F%B3%E6%B2%B9%E5%A4%A7%E5%AD%A6/7434895"

res = get(url, headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Charset": "utf-8", })

res.encoding = res.apparent_encoding

html = res.text
base_url = urlparse(url).scheme + "://" + urlparse(url).netloc
text = html2text(html, baseurl=base_url)

with open("nepu.md", "w", encoding="utf-8") as f:
    f.write(text)

# 使用另外一个库markdownify试试
from markdownify import markdownify

text = markdownify(html)
with open("nepu2.md", "w", encoding="utf-8") as f:
    f.write(text)
