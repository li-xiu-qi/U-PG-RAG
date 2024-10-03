import requests
import json

from app.serves.web_search.web_search import SearchResult, WebSearch


class BoSearch(WebSearch):
    def __init__(self, api_key):
        self.url = "https://api.bochaai.com/v1/web-search"
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

    def search(self, query, max_results) -> list[SearchResult]:
        payload = json.dumps({
            "query": query,
            "count": max_results
        })
        response = requests.request("POST", self.url, headers=self.headers, data=payload)
        if response.status_code != 200:
            return []
        results = response.json()
        json_data = json.loads(results)
        results = json_data["data"]["webPages"]["value"]
        return [SearchResult(title=r["name"], href=r["url"], body=r["snippet"]) for r in results]
