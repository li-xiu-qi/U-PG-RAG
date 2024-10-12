from requests import get

url = "https://www.nepu.edu.cn"

response = get(url)
response.encoding = response.apparent_encoding
print(response.text)
