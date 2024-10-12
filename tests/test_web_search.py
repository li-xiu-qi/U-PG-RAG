from app.serves.web_search.upg_search import UPGSearch
from tests.config import ServeConfig

if __name__ == "__main__":
    upg_search = UPGSearch(text_search_url=ServeConfig.text_search_url)
    results = upg_search.search("python", 100)
    for result in results:
        print(result.title)
        print(result.href)
        print(result.body)
        print()
