import requests
import chardet
from typing import Optional


class HTMLFetcher:
    def __init__(self, url: str, headers: Optional[dict] = None):
        self.url = url
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }

    def fetch_html(self) -> str:
        response = requests.get(self.url, headers=self.headers)
        content_type = response.headers.get('Content-Type', '')
        encoding_from_header = None
        if 'charset=' in content_type:
            encoding_from_header = content_type.split('charset=')[-1].strip().lower()

        encoding_from_chardet = chardet.detect(response.content)['encoding']

        if encoding_from_header:
            encoding = encoding_from_header
        elif encoding_from_chardet:
            encoding = encoding_from_chardet
        else:
            encoding = 'utf-8'

        return response.content.decode(encoding)
