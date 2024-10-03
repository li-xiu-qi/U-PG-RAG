from abc import ABC, abstractmethod
from pydantic import BaseModel


class SearchResult(BaseModel):
    title: str
    href: str
    body: str


class WebSearch(ABC):

    @abstractmethod
    def search(self, query, max_results) -> list[SearchResult]:
        pass
