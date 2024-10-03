import requests

from app.serves.web_search.web_search import SearchResult


class GoogleSearch:
    def __init__(self, api_key, cse_id):
        self.api_key = api_key
        self.cse_id = cse_id
        self.url = "https://www.googleapis.com/customsearch/v1"

    def search(self, query, max_results=10):
        params = {
            'q': query,
            'cx': self.cse_id,
            'key': self.api_key,
            'num': max_results
        }
        response = requests.get(self.url, params=params)
        if response.status_code != 200:
            return []
        results = response.json()
        if 'items' not in results:
            return []
        return [SearchResult(title=r["title"], href=r["link"], body=r["snippet"]) for r in results['items']]

