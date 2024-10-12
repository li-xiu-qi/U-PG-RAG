from pydantic import BaseModel, HttpUrl
from typing import List


class Url(BaseModel):
    url: HttpUrl
    title: str | None = ""


class LinkResource(BaseModel):
    url: HttpUrl | None = ""
    title: str | None = ""
    file_links: List[Url] = []
    image_links: List[Url] = []
    hypertext_links: List[Url] = []


def link_sort(data_type: str, link: HttpUrl, title: str, link_resource: LinkResource):
    """
    根据数据类型将带有标题的链接分类并存储到相应的列表中。

    :param data_type: 数据类型，如 'file', 'image', 'hypertext'
    :param link: 链接地址
    :param title: 链接的标题
    :param url_with_resources: 包含主URL和关联资源的实例
    """
    try:
        new_link = Url(url=link, title=title)
    except Exception as e:
        return

    if data_type == "file":
        link_resource.file_links.append(new_link)
    elif data_type == "image":
        link_resource.image_links.append(new_link)
    elif data_type == "hypertext":
        link_resource.hypertext_links.append(new_link)
