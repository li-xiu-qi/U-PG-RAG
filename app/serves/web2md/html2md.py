from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from markdownify import MarkdownConverter, abstract_inline_conversion, chomp

from app.serves.web2md.link_resource import LinkResource, link_sort


class Html2Md(MarkdownConverter):
    def __init__(self, current_url: str | None = None,
                 current_title: str | None = None,
                 link_resource: Optional[LinkResource] = None,
                 remove_links: bool = False, **kwargs):
        super().__init__(strip=['a', 'img'] if remove_links else [], **kwargs)
        self.current_url = current_url
        self.current_title = current_title
        self.convert_to_absolute = False or self.current_url
        self.link_resource = link_resource or LinkResource(url=self.current_url, title=self.current_title)
        self.remove_links = remove_links

    def convert_img(self, el, text, convert_as_inline):
        if self.remove_links:
            return ''

        alt_text = el.attrs.get('alt', '') or ''
        src_url = el.attrs.get('src', '') or ''
        title_text = el.attrs.get('title', '') or ''

        if title_text:
            escaped_title = title_text.replace('"', r'\"')
            title_part = f' "{escaped_title}"'
        else:
            title_part = ''

        if self.convert_to_absolute:
            if self.current_url is None:
                raise ValueError("current_url is required for convert_to_absolute")
            src_url = urljoin(self.current_url, src_url)

        if convert_as_inline and el.parent.name not in self.options['keep_inline_images_in']:
            return alt_text
        if not self.remove_links:
            link_sort("image", src_url, title_text, self.link_resource)
        return f'![{alt_text}]({src_url}{title_part})'

    def _process_table_element(self, element):
        soup = BeautifulSoup(str(element), 'html.parser')
        for tag in soup.find_all(True):
            attrs_to_keep = ['colspan', 'rowspan']
            tag.attrs = {key: value for key, value in tag.attrs.items() if key in attrs_to_keep}
        return str(soup)

    def convert_table(self, el, text, convert_as_inline):
        soup = BeautifulSoup(str(el), 'html.parser')
        has_colspan_or_rowspan = any(
            tag.has_attr('colspan') or tag.has_attr('rowspan') for tag in soup.find_all(['td', 'th']))

        if has_colspan_or_rowspan:
            return self._process_table_element(el)
        else:
            return super().convert_table(el, text, convert_as_inline)

    def convert_a(self, el, text, convert_as_inline):
        if self.remove_links:
            return ''

        prefix, suffix, text = chomp(text)
        if not text:
            return ''

        href_url = el.get('href')
        title_text = el.get('title')

        if self.convert_to_absolute:
            href_url = urljoin(self.current_url, href_url)
        if not self.remove_links:
            if href_url.endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx')):
                link_sort("file", href_url, title_text, self.link_resource)
            else:
                link_sort("hypertext", href_url, title_text, self.link_resource)

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
