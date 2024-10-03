from config import ServeConfig
from web_search import WebSearch, SearchResult
from requests import get


class UPGSearch(WebSearch):
    def __init__(self, text_search_url: str | None = None,
                 news_search_url: str | None = None):
        self.text_search_url = text_search_url or ServeConfig.text_search_url
        self.news_search_url = news_search_url or ServeConfig.news_search_url

    def search(self, query, max_results) -> list[SearchResult]:
        results = get(self.text_search_url, params={"keywords": query, "max_results": max_results}).json()
        return [SearchResult(title=result["title"], href=result["href"], body=result["body"]) for result in results]

    def news_search(self, query, max_results) -> list[SearchResult]:
        results = get(self.news_search_url, params={"keywords": query, "max_results": max_results}).json()
        return [SearchResult(title=result["title"], href=result["href"], body=result["body"]) for result in results]



if __name__ == "__main__":
    search = UPGSearch()
    results = search.search("东北石油大学的招生电话是多少", 5)
    print(results)
