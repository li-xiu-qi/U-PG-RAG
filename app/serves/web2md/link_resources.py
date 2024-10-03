from pydantic import BaseModel, HttpUrl
from typing import List


class LinkResources(BaseModel):
    file_links: List[HttpUrl] = []
    image_links: List[HttpUrl] = []
    hypertext_links: List[HttpUrl] = []


def link_sort(data_type: str, link: str, link_resources: LinkResources):
    if data_type == "file":
        link_resources.file_links.append(link)
    elif data_type == "image":
        link_resources.image_links.append(link)
    elif data_type == "hypertext":
        link_resources.hypertext_links.append(link)
