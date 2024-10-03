import os
import re
import logging
from typing import List, Optional

import aiofiles
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.image_operation import ImageOperation
from app.serves.file_processing.md_split import MarkdownHeaderTextSplitter, MarkdownTextRefSplitter, Chunk

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def nested_split_markdown(file_path: str,
                                text: str | None = None,
                                chunk_size: int = 832,
                                chunk_overlap: int = 32,
                                metadata: dict = {},
                                remove_image_tag: bool = True,
                                uri2remote: bool = False,
                                image_operator: Optional[ImageOperation] = None,
                                db: Optional[AsyncSession] = None
                                ) -> List[Chunk]:
    """首先按标题分割，然后按长度分割。

    `header` 应该作为内容的一部分。
    """
    logger.info(f"Starting nested_split_markdown for file: {file_path}")
    # 读取文件
    if text is not None:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
            text = await file.read()
    head_splitter = MarkdownHeaderTextSplitter()
    chunks = head_splitter.create_chunks(text, metadata=metadata)
    text_chunks = []

    text_ref_splitter = MarkdownTextRefSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
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

        if len(chunk.content_or_path) > chunk_size:
            sub_chunks = text_ref_splitter.create_chunks([chunk.content_or_path], [chunk.metadata])

            for sub_chunk in sub_chunks:
                if len(sub_chunk.content_or_path) >= 10:
                    sub_chunk.content_or_path = '{} {}'.format(header, sub_chunk.content_or_path.lower())
                    sub_chunk = await set_image_paths(sub_chunk, filepath=file_path, uri2remote=uri2remote,
                                                      image_operator=image_operator,
                                                      db=db)
                    if remove_image_tag:
                        sub_chunk = remove_image_tags(sub_chunk)
                    sub_chunk.metadata['paragraph_number'] = paragraph_counter
                    paragraph_counter += 1
                    text_chunks.append(sub_chunk)

        elif len(chunk.content_or_path) >= 10:
            chunk.content_or_path = '{} {}'.format(header, chunk.content_or_path.lower())
            chunk = await set_image_paths(chunk, filepath=file_path, uri2remote=uri2remote,
                                          image_operator=image_operator,
                                          db=db)
            if remove_image_tag:
                chunk = remove_image_tags(chunk)
            chunk.metadata['paragraph_number'] = paragraph_counter
            paragraph_counter += 1
            text_chunks.append(chunk)

    logger.info(f"Completed nested_split_markdown for file: {file_path}")
    return text_chunks


def remove_image_tags(chunk: Chunk) -> Chunk:
    """从md文本里面删除图像的标签，包含html和md的标签。"""
    logger.debug("Removing image tags from chunk")
    md_image_pattern = re.compile(r'!\[([^\]]+)\]\(([a-zA-Z0-9:/._~#-]+)?\)')
    html_image_pattern = re.compile(r'<img\s+[^>]*?src=["\']([^"\']*)["\'][^>]*>')
    chunk.content_or_path = md_image_pattern.sub('', chunk.content_or_path)
    chunk.content_or_path = html_image_pattern.sub('', chunk.content_or_path)
    return chunk


def extract_image_paths(content: str) -> List[str]:
    """从内容中提取所有图像路径。"""
    logger.debug("Extracting image paths from content")
    md_image_pattern = re.compile(r'\[([^\]]+)\]\(([a-zA-Z0-9:/._~#-]+)?\)')
    html_image_pattern = re.compile(r'<img\s+[^>]*?src=["\']([^"\']*)["\'][^>]*>')
    image_paths = md_image_pattern.findall(content) + html_image_pattern.findall(content)
    return [match[1] if isinstance(match, tuple) else match for match in image_paths]


def resolve_image_paths(image_paths: List[str], base_path: str) -> List[str]:
    """解析相对路径为绝对路径。"""
    logger.debug("Resolving image paths to absolute paths")
    resolved_paths = []
    for path in image_paths:
        if path and not os.path.isabs(path):
            path = os.path.join(base_path, path)
        resolved_paths.append(path)
    return resolved_paths


async def set_image_paths(chunk: Chunk, filepath: str,
                          uri2remote: bool = False,
                          image_operator: Optional[ImageOperation] = None,
                          db: Optional[AsyncSession] = None) -> Chunk:
    """将图像路径添加到元数据中。"""
    logger.debug("Setting image paths in chunk metadata")
    image_paths = extract_image_paths(chunk.content_or_path)
    resolved_paths = resolve_image_paths(image_paths, os.path.dirname(filepath))

    if any(os.path.exists(path) for path in resolved_paths):
        chunk.metadata.setdefault('image_paths', [])
        if uri2remote:
            if image_operator is None or db is None:
                raise ValueError('image_operator and db must not be None')

            for i, path in enumerate(resolved_paths):
                image_url = await image_operator.local_img2remote(db=db, file_path=path)
                resolved_paths[i] = image_url
        chunk.metadata['image_paths'] = resolved_paths

    return chunk


def clean_md(text: str):
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
