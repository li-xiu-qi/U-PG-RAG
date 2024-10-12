from typing import Union, Tuple

from app.serves.web2md.html2md import Html2Md
from app.serves.web2md.link_resource import LinkResource


class Web2md:
    def __init__(self, remove_links: bool = False, **options):
        self.options = options
        self.remove_links = remove_links

    def html2md(self, html_content: str,
                current_url: Union[str, None] = None,
                current_title: Union[str, None] = None,
                link_resource: LinkResource | None = None) -> Union[str, Tuple[str, LinkResource]]:
        link_resource = link_resource or LinkResource(url=current_url, title=current_title)
        markdown_content = Html2Md(
            current_url=current_url,
            current_title=current_title,
            link_resource=link_resource,
            remove_links=self.remove_links,
            **self.options
        ).convert(html_content)
        if self.remove_links:
            return markdown_content
        return markdown_content, link_resource

