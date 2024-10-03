import requests
import chardet
from markdownify import MarkdownConverter, abstract_inline_conversion, chomp
from urllib.parse import urljoin
from bs4 import BeautifulSoup
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


class CustomMarkdownConverter(MarkdownConverter):
    def __init__(self, current_url, link_resources: LinkResources | None = None, **kwargs):
        super().__init__(**kwargs)
        self.current_url = current_url
        self.convert_to_absolute = kwargs.get('convert_to_absolute', False)
        self.link_resources = link_resources or LinkResources()

    def convert_img(self, element, text, convert_as_inline):
        alt_text = element.attrs.get('alt', '') or ''
        src_url = element.attrs.get('src', '') or ''
        title_text = element.attrs.get('title', '') or ''

        if title_text:
            escaped_title = title_text.replace('"', r'\"')
            title_part = f' "{escaped_title}"'
        else:
            title_part = ''

        if self.convert_to_absolute:
            src_url = urljoin(self.current_url, src_url)

        link_sort("image", src_url, self.link_resources)
        if convert_as_inline and element.parent.name not in self.options['keep_inline_images_in']:
            return alt_text

        return f'![{alt_text}]({src_url}{title_part})'

    def _process_table_element(self, element):
        soup = BeautifulSoup(str(element), 'html.parser')
        for tag in soup.find_all(True):
            attrs_to_keep = ['colspan', 'rowspan']
            tag.attrs = {key: value for key, value in tag.attrs.items() if key in attrs_to_keep}
        return str(soup)

    def convert_table(self, element, text, convert_as_inline):
        soup = BeautifulSoup(str(element), 'html.parser')
        has_colspan_or_rowspan = any(
            tag.has_attr('colspan') or tag.has_attr('rowspan') for tag in soup.find_all(['td', 'th']))

        if has_colspan_or_rowspan:
            return self._process_table_element(element)
        else:
            return super().convert_table(element, text, convert_as_inline)

    def convert_a(self, element, text, convert_as_inline):
        prefix, suffix, text = chomp(text)
        if not text:
            return ''
        href_url = element.get('href')
        title_text = element.get('title')

        if self.convert_to_absolute:
            href_url = urljoin(self.current_url, href_url)

        if href_url.endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx')):
            link_sort("file", href_url, self.link_resources)
        else:
            link_sort("hypertext", href_url, self.link_resources)

        if (self.options['autolinks']
                and text.replace(r'\_', '_') == href_url
                and not title_text
                and not self.options['default_title']):
            return f'<{href_url}>'
        if self.options['default_title'] and not title_text:
            title_text = href_url

        if title_text:
            escaped_title = title_text.replace('"', r'\"')
            title_part = f' "{escaped_title}"'
        else:
            title_part = ''

        return f'{prefix}[{text}]({href_url}{title_part}){suffix}' if href_url else text

    convert_b = abstract_inline_conversion(lambda self: 2 * self.options['strong_em_symbol'])


def html2md(html_content, current_url, link_resources, **options):
    return CustomMarkdownConverter(current_url=current_url, link_resources=link_resources, **options).convert(
        html_content)


def fetch_and_convert(url, headers=None, **options):
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }

    response = requests.get(url, headers=headers)

    content_type = response.headers.get('Content-Type', '')
    encoding_from_header = None
    if 'charset=' in content_type:
        encoding_from_header = content_type.split('charset=')[-1].strip().lower()

    encoding_from_chardet = chardet.detect(response.content)['encoding']

    if encoding_from_header:
        encoding = encoding_from_header
    elif encoding_from_chardet:
        encoding = encoding_from_chardet
    else:
        encoding = 'utf-8'

    html_content = response.content.decode(encoding)
    link_resources = LinkResources()
    markdown_content = html2md(html_content, current_url=url, link_resources=link_resources, **options)
    return markdown_content, link_resources


# 示例用法
html_content = """
<html>
<body>
<img src="/path/to/image.jpg" alt="示例图片">
<img src="/path/to/image2.jpg" alt="aljfkajd">
<a href="/path/to/page">示例链接</a>
<a href="/path/to/page2">aljfkajd</a>
<a href="/path/to/file.pdf">文件链接</a>
<table>
    <tr>
        <td colspan="2">Cell with colspan</td>
    </tr>
    <tr>
        <td>Cell 1</td>
        <td>Cell 2</td>
    </tr>
</table>
</body>
</html>
"""

# 假设这是当前页面的完整 URL
current_url = "https://example.com/some/page.html"

# 将 HTML 转换为 Markdown 并分类内容
markdown_content, link_resources = fetch_and_convert(current_url, convert_to_absolute=True)

# print(markdown_content)
print(link_resources)
