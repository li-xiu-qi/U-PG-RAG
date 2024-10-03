from web2md.custom_markdown_converter import CustomMarkdownConverter
from web2md.link_resources import LinkResources
from web2md.html_fetcher import HTMLFetcher


class Web2md:
    def __init__(self, remove_links: bool = False, **options):
        self.options = options
        self.remove_links = remove_links

    def convert_html_to_markdown(self, html_content: str, current_url: str | None = None) -> (str, LinkResources):
        link_resources = LinkResources()
        markdown_content = CustomMarkdownConverter(
            current_url=current_url,
            link_resources=link_resources,
            remove_links=self.remove_links,
            **self.options
        ).convert(html_content)
        return markdown_content, link_resources

    def fetch_and_convert(self, url: str) -> (str, LinkResources):
        fetcher = HTMLFetcher(url)
        html_content = fetcher.fetch_html()
        return self.convert_html_to_markdown(html_content, current_url=url)




