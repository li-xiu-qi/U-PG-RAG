import asyncio
import hashlib
import json
import logging
import os
import uuid
from typing import AsyncGenerator, Optional, Dict, List
from urllib.parse import urlparse, urljoin

import diskcache
import dotenv
import requests
from bs4 import BeautifulSoup
from diskcache import Cache
from htmldate import find_date
from pydantic import BaseModel

from app.serves.fetch_web_resouece.random_agent import get_useragent

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FILE_SUFFIX_TYPES = [
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'csv', 'zip', 'rar', 'gz', 'tgz', 'tar', '7z'
]


class URL(BaseModel):
    url: str | None = ""
    title: str | None = ""


class UrlResource(BaseModel):
    image_urls: List[URL]
    file_urls: List[URL]


class SearchResult(BaseModel):
    url: str | None = ""
    favicon: str | None = ""
    title: str | None = ""
    description: str | None = ""
    media: str | None = ""
    html_content: str | None = ""
    publish_date: str | None = ""
    url_resource: UrlResource | None = None


class CacheManager:
    def __init__(self, cache: Optional[Cache] = None, expire: int = 3600 * 24):
        self.cache = cache or Cache(directory='./html_cache', eviction_policy='least-recently-used')
        self.expire = expire

    def _get_url_hash(self, url: str) -> str:
        return hashlib.md5(url.encode('utf-8')).hexdigest()

    def get_cached_html(self, url: str) -> Optional[str]:
        url_hash = self._get_url_hash(url)
        return self.cache.get(url_hash) if self.cache else None

    def set_cached_html(self, url: str, html_content: str) -> None:
        url_hash = self._get_url_hash(url)
        if self.cache:
            self.cache.set(url_hash, html_content, expire=self.expire)


class HTMLFetcher:
    def __init__(self, headers: Optional[Dict[str, str]] = None, cache: Optional[diskcache.Cache] = None,
                 max_concurrent_per_domain: int = 5):
        self.headers = headers or self._default_headers()
        self.cache_manager = CacheManager(cache)
        self.max_concurrent_per_domain = max_concurrent_per_domain
        self.domain_semaphores: Dict[str, asyncio.Semaphore] = {}

    @staticmethod
    def _default_headers() -> Dict[str, str]:
        return {
            "User-Agent": get_useragent(),
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Accept": "*/*",
            "Accept-Charset": "utf-8",
        }

    def _get_semaphore_for_domain(self, domain: str) -> asyncio.Semaphore:
        if domain not in self.domain_semaphores:
            self.domain_semaphores[domain] = asyncio.Semaphore(self.max_concurrent_per_domain)
        return self.domain_semaphores[domain]

    async def _fetch_html(self, search_result: SearchResult, timeout: int = 5) -> SearchResult:
        url = search_result.url
        cached_html = self.cache_manager.get_cached_html(url)
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"

        if cached_html:
            return self._update_search_result(search_result, cached_html, base_url)

        self.headers["Referer"] = base_url

        try:
            response = requests.get(url, headers=self.headers, timeout=timeout)
            response.encoding = response.apparent_encoding
            html_content = response.text
            self.cache_manager.set_cached_html(url, html_content)
            return self._update_search_result(search_result, html_content, base_url)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                logger.error(f"404 Not Found: {url}")
            else:
                logger.error(f"HTTP Error {e.response.status_code}: {e.response.reason}")
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection Error: {url}")
        except requests.exceptions.Timeout:
            logger.error(f"Timeout Error: {url}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
        return search_result

    def _update_search_result(self, search_result: SearchResult, html_content: str, base_url: str) -> SearchResult:
        soup = BeautifulSoup(html_content, 'html.parser')
        for tag in soup.find_all(['a', 'img', 'link', 'script']):
            if tag.name == 'a' and tag.get('href'):
                tag['href'] = urljoin(base_url, tag['href'])
            elif tag.name == 'img' and tag.get('src'):
                tag['src'] = urljoin(base_url, tag['src'])
            elif tag.name == 'link' and tag.get('href'):
                tag['href'] = urljoin(base_url, tag['href'])
            elif tag.name == 'script' and tag.get('src'):
                tag['src'] = urljoin(base_url, tag['src'])
        search_result.html_content = str(soup)
        search_result.publish_date = find_date(html_content)
        search_result.url_resource = self._extract_urls(html_content, base_url)
        return search_result

    def _extract_urls(self, html_content: str, base_url: str) -> UrlResource:
        soup = BeautifulSoup(html_content, 'html.parser')
        image_urls_set = {urljoin(base_url, img['src']) for img in soup.find_all('img', src=True)}
        file_urls = []

        # for a in soup.find_all('a', href=True):
        #     href = a['href'].lower()
        #     if any(href.endswith(suffix) for suffix in FILE_SUFFIX_TYPES):
        #         file_urls.append(URL(url=urljoin(base_url, a['href']), title=a.get_text(strip=True)))

        image_urls = [URL(url=url, title='') for url in image_urls_set]
        return UrlResource(image_urls=image_urls, file_urls=file_urls)

    async def fetch_html_batch(self, results: List[SearchResult], timeout: int = 5) -> AsyncGenerator[
        SearchResult, None]:
        tasks = [self._fetch_html(result, timeout) for result in results]
        for task in asyncio.as_completed(tasks):
            result = await task
            # 没有获取到发布日期的，说明是爬取失败了，不返回
            if result.publish_date:
                yield result


class ZhiPuWebSearch:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("API_KEY")

    def search(self, query: str) -> List[SearchResult]:
        msg = [{"role": "user", "content": query}]
        tool = "web-search-pro"
        url = "https://open.bigmodel.cn/api/paas/v4/tools"
        request_id = str(uuid.uuid4())
        data = {
            "request_id": request_id,
            "tool": tool,
            "stream": False,
            "messages": msg
        }

        resp = requests.post(url, json=data, headers={'Authorization': self.api_key}, timeout=300)
        web_search_result = json.loads(resp.content.decode())
        choices = web_search_result["choices"][0]
        finish_reason = choices["finish_reason"]

        if finish_reason == "stop":
            message = choices["message"]
            tool_calls = message["tool_calls"]
            search_results = tool_calls[1]["search_result"]

            return [SearchResult(
                url=search_result.get("link", ""),
                favicon=search_result.get("icon", ""),
                media=search_result.get("media", ""),
                title=search_result.get("title", ""),
                description=search_result.get("content", "")
            ) for search_result in search_results]
        else:
            return []


async def main():
    search_engine = ZhiPuWebSearch()
    results = search_engine.search("东北石油大学保研规则是什么？ site:nepu.edu.cn")
    print(results)
    # cache = diskcache.Cache('./html_cache')
    # fetcher = HTMLFetcher(cache=cache, max_concurrent_per_domain=5)
    #
    # enriched_results = fetcher.fetch_html_batch(results, timeout=5)
    #
    # async for result in enriched_results:
    #     print(result)


if __name__ == "__main__":
    asyncio.run(main())
