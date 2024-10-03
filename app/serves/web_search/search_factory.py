from app.serves.web_search.bo_search import BoSearch
from app.serves.web_search.ddg_search import DDGSearch
from app.serves.web_search.google_search import GoogleSearch
from app.serves.web_search.upg_search import UPGSearch
from app.serves.web_search.web_search import SearchResult


class SearchFactory:
    def __init__(self, engine_type):
        self.engine_type = engine_type

    def search(self, query, max_results, **kwargs) -> list[SearchResult]:
        if self.engine_type == "DDG":
            return DDGSearch().search(query, max_results)
        elif self.engine_type == "UPG":
            return UPGSearch().search(query, max_results)
        elif self.engine_type == "UPG_NEWS":
            return UPGSearch().news_search(query, max_results)
        elif self.engine_type == "BO":
            api_key = kwargs.get("api_key")
            if not api_key:
                raise ValueError("BO API key is required")
            return BoSearch(api_key=api_key).search(query, max_results)
        elif self.engine_type == "GOOGLE":
            api_key = kwargs.get("api_key")
            cse_id = kwargs.get("cse_id")
            if not api_key or not cse_id:
                raise ValueError("Google API key and CSE ID are required")
            return GoogleSearch(api_key=api_key, cse_id=cse_id).search(query, max_results)
        else:
            raise ValueError("Invalid search engine type")
