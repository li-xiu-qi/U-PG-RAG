import requests
from goose3 import Goose

# url = "https://www.nepu.edu.cn"
url = "https://xsc.nepu.edu.cn/info/1287/3616.htm"
# url = "https://baike.baidu.com/item/%E4%B8%9C%E5%8C%97%E7%9F%B3%E6%B2%B9%E5%A4%A7%E5%AD%A6/7434895"
response = requests.get(url)
response.encoding = response.apparent_encoding
html = response.text

g = Goose()
article = g.extract(raw_html=html)
content = article.cleaned_text

print(content)
