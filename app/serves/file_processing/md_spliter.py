import os
import re
import logging
from typing import List, Optional

import aiofiles
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.image_operation import ImageOperation
from app.serves.file_processing.split import MarkdownHeaderTextSplitter, MarkdownTextRefSplitter, Chunk

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class MarkdownSpliter:
    def __init__(self,
                 chunk_size: int = 832,
                 chunk_overlap: int = 32,
                 remove_image_tag: bool = True,
                 uri2remote: bool = False):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.remove_image_tag = remove_image_tag
        self.uri2remote = uri2remote
        self.all_links = []

    async def nested_split_markdown(self,
                                    text: str | None = None,
                                    file_path: str | None = None,
                                    metadata: dict = {},
                                    image_operator: Optional[ImageOperation] = None,
                                    db: Optional[AsyncSession] = None) -> List[Chunk]:
        """首先按标题分割，然后按长度分割。

        `header` 应该作为内容的一部分。
        """
        logger.info(f"Starting nested_split_markdown for file: {file_path}")
        # 读取文件
        if not text:
            if not file_path:
                raise ValueError('file_path must not be None')
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                text = await file.read()
        head_splitter = MarkdownHeaderTextSplitter()
        chunks = head_splitter.create_chunks(text, metadata=metadata)
        text_chunks = []

        text_ref_splitter = MarkdownTextRefSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        paragraph_counter = 1

        for chunk in chunks:
            header = ''
            if 'Header 1' in chunk.metadata:
                header += chunk.metadata['Header 1']
            if 'Header 2' in chunk.metadata:
                header += ' '
                header += chunk.metadata['Header 2']
            if 'Header 3' in chunk.metadata:
                header += ' '
                header += chunk.metadata['Header 3']

            if len(chunk.content) > self.chunk_size:
                sub_chunks = text_ref_splitter.create_chunks([chunk.content], [chunk.metadata])

                for sub_chunk in sub_chunks:
                    if len(sub_chunk.content) >= 10:
                        sub_chunk.content = '{} {}'.format(header, sub_chunk.content.lower())
                        sub_chunk = await self.set_image_paths(sub_chunk,
                                                               file_path=file_path,
                                                               image_operator=image_operator,
                                                               db=db)
                        if self.remove_image_tag:
                            sub_chunk = self.remove_image_tags(sub_chunk)
                        sub_chunk.metadata['paragraph_number'] = paragraph_counter
                        paragraph_counter += 1
                        text_chunks.append(sub_chunk)

            elif len(chunk.content) >= 10:
                chunk.content = '{} {}'.format(header, chunk.content.lower())
                chunk = await self.set_image_paths(chunk,
                                                   file_path=file_path,
                                                   image_operator=image_operator,
                                                   db=db)
                if self.remove_image_tag:
                    chunk = self.remove_image_tags(chunk)
                chunk.metadata['paragraph_number'] = paragraph_counter
                paragraph_counter += 1
                text_chunks.append(chunk)

        logger.info(f"Completed nested_split_markdown for file: {file_path}")
        return text_chunks

    def remove_image_tags(self, chunk: Chunk) -> Chunk:
        """从md文本里面删除图像的标签，包含html和md的标签。"""
        logger.debug("Removing image tags from chunk")
        md_image_pattern = re.compile(r'!\[([^\]]+)\]\(([a-zA-Z0-9:/._~#-]+)?\)')
        html_image_pattern = re.compile(r'<img\s+[^>]*?src=["\']([^"\']*)["\'][^>]*>')
        chunk.content = md_image_pattern.sub('', chunk.content)
        chunk.content = html_image_pattern.sub('', chunk.content)
        return chunk

    def extract_image_paths(self, content: str) -> List[str]:
        """从内容中提取所有图像路径。"""
        logger.debug("Extracting image paths from content")
        md_image_pattern = re.compile(r'\[([^\]]+)\]\(([a-zA-Z0-9:/._~#-]+)?\)')
        html_image_pattern = re.compile(r'<img\s+[^>]*?src=["\']([^"\']*)["\'][^>]*>')
        image_paths = md_image_pattern.findall(content) + html_image_pattern.findall(content)
        return [match[1] if isinstance(match, tuple) else match for match in image_paths]

    def resolve_image_paths(self, image_paths: List[str], file_path: str | None = None) -> List[str]:
        """解析相对路径为绝对路径，保留远程链接和绝对路径。"""
        logger.debug("Resolving image paths to absolute paths")
        resolved_paths = []
        for path in image_paths:
            if path.startswith(('http://', 'https://')):
                resolved_paths.append(path)
            elif os.path.isabs(path):
                resolved_paths.append(path)
            else:
                if file_path:
                    os.path.dirname(file_path)
                    path = os.path.join(file_path, path)
                resolved_paths.append(path)
        return resolved_paths

    async def set_image_paths(self, chunk: Chunk, file_path: str | None = None,
                              image_operator: Optional[ImageOperation] = None,
                              db: Optional[AsyncSession] = None) -> Chunk:
        """将图像路径添加到元数据中。"""
        logger.debug("Setting image paths in chunk metadata")
        image_paths = self.extract_image_paths(chunk.content)
        resolved_paths = self.resolve_image_paths(image_paths, file_path=file_path)

        if any(os.path.exists(path) for path in resolved_paths):
            chunk.metadata.setdefault('image_paths', [])
            if self.uri2remote:
                if image_operator is None or db is None:
                    raise ValueError('image_operator and db must not be None')

                for i, path in enumerate(resolved_paths):
                    image_url = await image_operator.local_img2remote(db=db, file_path=path)
                    resolved_paths[i] = image_url
            chunk.metadata['image_paths'] = resolved_paths

        return chunk

    def clean_md(self, text: str):
        """去除 Markdown 文档中不包含关键问题词的部分，如代码块、URL 链接等。"""
        logger.debug("Cleaning markdown content")
        # 去除引用
        pattern_ref = r'\[(.*?)\]\(.*?\)'
        new_text = re.sub(pattern_ref, r'\1', text)

        # 去除代码块
        pattern_code = r'```.*?```'
        new_text = re.sub(pattern_code, '', new_text, flags=re.DOTALL)

        # 去除下划线
        new_text = re.sub('_{5,}', '', new_text)

        # 使用小写
        new_text = new_text.lower()
        return new_text

    def extract_all_links(self, content: str) -> List[str]:
        """从内容中提取所有链接。"""
        logger.debug("Extracting all links from content")
        md_link_pattern = re.compile(r'\[([^\]]+)\]\(([a-zA-Z0-9:/._~#-]+)?\)')
        html_link_pattern = re.compile(r'<a\s+[^>]*?href=["\']([^"\']*)["\'][^>]*>')
        links = md_link_pattern.findall(content) + html_link_pattern.findall(content)
        self.all_links = [match[1] if isinstance(match, tuple) else match for match in links]
        return self.all_links
