from abc import ABC, abstractmethod
from pydantic import BaseModel


class SearchResult(BaseModel):
    title: str
    url: str
    description: str
    date: str | None = ""
    favicon: str | None = ""


class WebSearch(ABC):

    @abstractmethod
    def search(self, query, max_results) -> list[SearchResult]:
        pass
