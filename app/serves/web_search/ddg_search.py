from duckduckgo_search import DDGS

from app.serves.web_search.web_search_base import WebSearch, SearchResult


class DDGSearch(WebSearch):
    def search(self, query, max_results) -> list[SearchResult]:
        results = DDGS().text(keywords=query, max_results=max_results)
        return [SearchResult(title=result["title"], href=result["href"], body=result["body"]) for result in results]
