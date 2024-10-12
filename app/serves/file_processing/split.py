# 从  https://github.com/InternLM/HuixiangDou 修改而来
import copy
import re
from abc import ABC, abstractmethod
from typing import (Any, Callable, Dict, Iterable,
                    List, Literal, Optional, Tuple, Union)

from loguru import logger

from app.serves.file_processing.split_model import Chunk, LineType, HeaderType


class TextSplitter(ABC):
    """文本分割接口，用于将文本分割成多个块。"""

    def __init__(
            self,
            chunk_size: int = 832,
            chunk_overlap: int = 32,
            length_function: Callable[[str], int] = len,
            keep_separator: Union[bool, Literal['start', 'end']] = False,
            add_start_index: bool = False,
            strip_whitespace: bool = True,
    ) -> None:
        """创建一个新的 TextSplitter。

        Args:
            chunk_size: 返回块的最大大小
            chunk_overlap: 块之间的重叠字符数
            length_function: 测量给定块长度的函数
            keep_separator: 是否保留分隔符，并将其放置在每个对应块的位置（True='start'）
            add_start_index: 如果为 `True`，则在元数据中包含块的起始索引
            strip_whitespace: 如果为 `True`，则从每个块的开头和结尾去除空白字符
        """
        if chunk_overlap > chunk_size:
            raise ValueError(
                f'得到的块重叠 ({chunk_overlap}) 大于块大小 ({chunk_size})，应该更小。')
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._length_function = length_function
        self._keep_separator = keep_separator
        self._add_start_index = add_start_index
        self._strip_whitespace = strip_whitespace

    @abstractmethod
    def split_text(self, text: str) -> List[str]:
        """将文本分割成多个部分。"""

    def create_chunks(self,
                      texts: List[str],
                      metadatas: Optional[List[dict]] = None) -> List[Chunk]:
        """从文本列表创建块。"""
        _metadatas = metadatas or [{}] * len(texts)
        chunks = []
        for i, text in enumerate(texts):
            index = 0
            previous_chunk_len = 0
            for chunk in self.split_text(text):
                metadata = copy.deepcopy(_metadatas[i])
                if self._add_start_index:
                    offset = index + previous_chunk_len - self._chunk_overlap
                    index = text.find(chunk, max(0, offset))
                    metadata['start_index'] = index
                    previous_chunk_len = len(chunk)
                new_chunk = Chunk(content=chunk, metadata=metadata)
                chunks.append(new_chunk)
        return chunks

    def _join_chunks(self, chunks: List[str], separator: str) -> Optional[str]:
        text = separator.join(chunks)
        if self._strip_whitespace:
            text = text.strip()
        if text == '':
            return None
        else:
            return text

    def _merge_splits(self, splits: Iterable[str], separator: str) -> List[str]:
        # 获取分隔符的长度
        separator_len = self._length_function(separator)

        # 初始化结果块列表和当前块
        chunks = []
        current_chunk: List[str] = []
        total = 0

        # 遍历所有的分割片段
        for d in splits:
            _len = self._length_function(d)

            # 如果当前块的总长度加上新片段的长度超过了块大小限制
            if (total + _len + (separator_len if len(current_chunk) > 0 else 0) > self._chunk_size):
                # 如果当前块的总长度已经超过了块大小限制，发出警告
                if total > self._chunk_size:
                    logger.warning(
                        f'创建了一个大小为 {total} 的块，'
                        f'这比指定的 {self._chunk_size} 要长'
                    )
                # 如果当前块不为空，将其合并并添加到结果块列表中
                if len(current_chunk) > 0:
                    chunk = self._join_chunks(current_chunk, separator)
                    if chunk is not None:
                        chunks.append(chunk)
                    # 如果当前块的总长度超过了块重叠大小，或者当前块不为空且长度很长
                    while total > self._chunk_overlap or (total + _len + (
                            separator_len if len(current_chunk) > 0 else 0) > self._chunk_size and total > 0):
                        # 从当前块的开头移除片段，直到满足条件
                        total -= self._length_function(current_chunk[0]) + (
                            separator_len if len(current_chunk) > 1 else 0)
                        current_chunk = current_chunk[1:]
            # 将新片段添加到当前块
            current_chunk.append(d)
            total += _len + (separator_len if len(current_chunk) > 1 else 0)

        # 将最后一个块合并并添加到结果块列表中
        chunk = self._join_chunks(current_chunk, separator)
        if chunk is not None:
            chunks.append(chunk)

        return chunks


def _split_text_with_regex(
        text: str, separator: str,
        keep_separator: Union[bool, Literal['start', 'end']]) -> List[str]:
    # 现在我们有了分隔符，分割文本
    if separator:
        if keep_separator:
            # 模式中的括号将分隔符保留在结果中。
            _splits = re.split(f'({separator})', text)
            splits = (([
                _splits[i] + _splits[i + 1]
                for i in range(0,
                               len(_splits) - 1, 2)
            ]) if keep_separator == 'end' else ([
                _splits[i] + _splits[i + 1] for i in range(1, len(_splits), 2)
            ]))
            if len(_splits) % 2 == 0:
                splits += _splits[-1:]
            splits = ((splits + [_splits[-1]]) if keep_separator == 'end' else
                      ([_splits[0]] + splits))
        else:
            splits = re.split(separator, text)
    else:
        splits = list(text)
    return [s for s in splits if s != '']


class CharacterTextSplitter(TextSplitter):
    """按字符分割文本。"""

    def __init__(self,
                 separator: str = '\n\n',
                 is_separator_regex: bool = False,
                 **kwargs: Any) -> None:
        """创建一个新的 TextSplitter。"""
        super().__init__(**kwargs)
        self._separator = separator
        self._is_separator_regex = is_separator_regex

    def split_text(self, text: str) -> List[str]:
        """分割传入的文本并返回块。"""
        # 首先我们天真地将大输入分割成一堆小的。
        separator = (self._separator if self._is_separator_regex else
                     re.escape(self._separator))
        splits = _split_text_with_regex(text, separator, self._keep_separator)
        _separator = '' if self._keep_separator else self._separator
        return self._merge_splits(splits, _separator)


class RecursiveCharacterTextSplitter(TextSplitter):
    """按递归字符分割文本。

    递归尝试按不同字符分割，找到一个可行的方法。
    """

    def __init__(
            self,
            separators: Optional[List[str]] = None,
            keep_separator: bool = True,
            is_separator_regex: bool = False,
            **kwargs: Any,
    ) -> None:
        """创建一个新的 TextSplitter。"""
        super().__init__(keep_separator=keep_separator, **kwargs)
        self._separators = separators or ['\n\n', '\n', ' ', '']
        self._is_separator_regex = is_separator_regex

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """分割传入的文本并返回块。"""
        final_chunks = []
        # 获取合适的分隔符
        separator = separators[-1]
        new_separators = []
        for i, _s in enumerate(separators):
            _separator = _s if self._is_separator_regex else re.escape(_s)
            if _s == '':
                separator = _s
                break
            if re.search(_separator, text):
                separator = _s
                new_separators = separators[i + 1:]
                break

        _separator = separator if self._is_separator_regex else re.escape(
            separator)
        splits = _split_text_with_regex(text, _separator, self._keep_separator)

        # 现在递归地合并较长的文本。
        _good_splits = []
        _separator = '' if self._keep_separator else separator
        for s in splits:
            if self._length_function(s) < self._chunk_size:
                _good_splits.append(s)
            else:
                if _good_splits:
                    merged_text = self._merge_splits(_good_splits, _separator)
                    final_chunks.extend(merged_text)
                    _good_splits = []
                if not new_separators:
                    final_chunks.append(s)
                else:
                    other_info = self._split_text(s, new_separators)
                    final_chunks.extend(other_info)
        if _good_splits:
            merged_text = self._merge_splits(_good_splits, _separator)
            final_chunks.extend(merged_text)
        return final_chunks

    def split_text(self, text: str) -> List[str]:
        return self._split_text(text, self._separators)


class ChineseRecursiveTextSplitter(RecursiveCharacterTextSplitter):

    def __init__(
            self,
            separators: Optional[List[str]] = None,
            keep_separator: bool = True,
            is_separator_regex: bool = True,
            **kwargs: Any,
    ) -> None:
        """创建一个新的 TextSplitter。"""
        super().__init__(keep_separator=keep_separator, **kwargs)
        self._separators = separators or [
            '\n\n', '\n', '。|！|？', '\.\s|\!\s|\?\s', '；|;\s', '，|,\s'
        ]
        self._is_separator_regex = is_separator_regex

    def _split_text_with_regex_from_end(self, text: str, separator: str,
                                        keep_separator: bool) -> List[str]:
        # 现在我们有了分隔符，分割文本
        if separator:
            if keep_separator:
                # 模式中的括号将分隔符保留在结果中。
                _splits = re.split(f'({separator})', text)
                splits = [
                    ''.join(i) for i in zip(_splits[0::2], _splits[1::2])
                ]
                if len(_splits) % 2 == 1:
                    splits += _splits[-1:]
                # splits = [_splits[0]] + splits
            else:
                splits = re.split(separator, text)
        else:
            splits = list(text)
        return [s for s in splits if s != '']

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """分割传入的文本并返回块。"""
        final_chunks = []
        # 获取合适的分隔符
        separator = separators[-1]
        new_separators = []
        for i, _s in enumerate(separators):
            _separator = _s if self._is_separator_regex else re.escape(_s)
            if _s == '':
                separator = _s
                break
            if re.search(_separator, text):
                separator = _s
                new_separators = separators[i + 1:]
                break

        _separator = separator if self._is_separator_regex else re.escape(
            separator)
        splits = self._split_text_with_regex_from_end(text, _separator,
                                                      self._keep_separator)

        # 现在递归地合并较长的文本。
        _good_splits = []
        _separator = '' if self._keep_separator else separator
        for s in splits:
            if self._length_function(s) < self._chunk_size:
                _good_splits.append(s)
            else:
                if _good_splits:
                    merged_text = self._merge_splits(_good_splits, _separator)
                    final_chunks.extend(merged_text)
                    _good_splits = []
                if not new_separators:
                    final_chunks.append(s)
                else:
                    other_info = self._split_text(s, new_separators)
                    final_chunks.extend(other_info)
        if _good_splits:
            merged_text = self._merge_splits(_good_splits, _separator)
            final_chunks.extend(merged_text)
        return [
            re.sub(r'\n{2,}', '\n', chunk.strip()) for chunk in final_chunks
            if chunk.strip() != ''
        ]


class MarkdownTextRefSplitter(RecursiveCharacterTextSplitter):
    """尝试按 Markdown 格式的标题分割文本。"""

    def __init__(self, **kwargs: Any) -> None:
        """初始化一个 MarkdownTextRefSplitter。"""
        separators = [
            # 首先，尝试按 Markdown 标题分割（从二级标题开始）
            '\n#{1,6} ',
            # 注意下面的替代语法没有在这里处理
            # 二级标题
            # ---------------
            # 代码块结束
            '```\n',
            # 水平线
            '\n\\*\\*\\*+\n',
            '\n---+\n',
            '\n___+\n',
            '\n\n',
            '\n',
            ' ',
            ''
        ]
        super().__init__(separators=separators, **kwargs)


class MarkdownHeaderTextSplitter:
    """基于指定的标题分割 Markdown 文件。"""

    def __init__(
            self,
            headers_to_split_on: List[Tuple[str, str]] = [
                ('#', 'Header 1'),
                ('##', 'Header 2'),
                ('###', 'Header 3'),
            ],
            strip_headers: bool = True,
    ):
        """创建一个新的 MarkdownHeaderTextSplitter。

        Args:
            headers_to_split_on: 我们想要跟踪的标题
            strip_headers: 从块的内容中去除分割的标题
        """
        # 给定我们想要分割的标题，
        # （例如，"#", "##" 等）按长度排序
        self.headers_to_split_on = sorted(
            headers_to_split_on, key=lambda split: len(split[0]), reverse=True
        )
        # 从块的内容中去除分割的标题
        self.strip_headers = strip_headers
        super().__init__()

    def aggregate_lines_to_chunks(self, lines: List[LineType],
                                  base_meta: dict) -> List[Chunk]:
        """将具有相同元数据的行合并成块
        Args:
            lines: 文本行 / 关联的标题元数据
        """
        aggregated_chunks: List[LineType] = []

        for line in lines:
            if (
                    aggregated_chunks
                    and aggregated_chunks[-1]["metadata"] == line["metadata"]
            ):

                # 如果聚合列表中的最后一行
                # 具有与当前行相同的元数据，
                # 将当前内容附加到最后一行的内容
                aggregated_chunks[-1]["content"] += "  \n" + line["content"]
            elif (
                    aggregated_chunks
                    and aggregated_chunks[-1]["metadata"] != line["metadata"]
                    # 如果其他元数据存在可能会有问题
                    and len(aggregated_chunks[-1]["metadata"]) < len(line["metadata"])
                    and aggregated_chunks[-1]["content"].split("\n")[-1][0] == "#"
                    and not self.strip_headers
            ):
                # 如果聚合列表中的最后一行
                # 具有与当前行不同的元数据，
                # 并且具有比当前行更浅的标题级别，
                # 并且最后一行是标题，
                # 并且我们不剥离标题，
                # 将当前内容附加到最后一行的内容
                aggregated_chunks[-1]["content"] += "  \n" + line["content"]
                # 并更新最后一行的元数据
                aggregated_chunks[-1]["metadata"] = line["metadata"]

            else:
                # 否则，将当前行附加到聚合列表
                aggregated_chunks.append(line)

        return [
            Chunk(content=chunk["content"],
                  metadata=dict(chunk['metadata'], **base_meta))
            for chunk in aggregated_chunks
        ]

    def create_chunks(self, text: str, metadata: dict = {}) -> List[Chunk]:
        """分割 Markdown 文件
        Args:
            text: Markdown 文件
        """

        # 按换行符 ("\n") 分割输入文本。
        lines = text.split("\n")
        # 最终输出
        lines_with_metadata: List[LineType] = []
        # 当前正在处理的块的内容和元数据
        current_content: List[str] = []
        current_metadata: Dict[str, str] = {}
        # 跟踪嵌套的标题结构
        header_stack: List[HeaderType] = []
        initial_metadata: Dict[str, str] = {}

        in_code_block = False
        opening_fence = ""

        for line in lines:
            stripped_line = line.strip()
            # 从字符串中去除所有不可打印字符，只保留可见文本。
            stripped_line = "".join(filter(str.isprintable, stripped_line))
            if not in_code_block:
                # 排除内联代码段
                if stripped_line.startswith("```") and stripped_line.count("```") == 1:
                    in_code_block = True
                    opening_fence = "```"
                elif stripped_line.startswith("~~~"):
                    in_code_block = True
                    opening_fence = "~~~"
            else:
                if stripped_line.startswith(opening_fence):
                    in_code_block = False
                    opening_fence = ""

            if in_code_block:
                current_content.append(stripped_line)
                continue

            # 检查每一行是否以我们想要分割的标题开头
            for sep, name in self.headers_to_split_on:
                # 检查行是否以标题开头
                if stripped_line.startswith(sep) and (
                        # 标题没有文本或标题后跟空格
                        # 这两个条件都是 sep 被用作标题的有效条件
                        len(stripped_line) == len(sep) or stripped_line[len(sep)] == " "
                ):
                    # 确保我们跟踪标题作为元数据
                    if name is not None:
                        # 获取当前标题级别
                        current_header_level = sep.count("#")

                        # 从堆栈中弹出较低或相同级别的标题
                        while (
                                header_stack
                                and header_stack[-1]["level"] >= current_header_level
                        ):
                            # 我们遇到了一个新的标题
                            # 在相同或更高级别
                            popped_header = header_stack.pop()
                            # 清除弹出标题的元数据
                            if popped_header["name"] in initial_metadata:
                                initial_metadata.pop(popped_header["name"])

                        # 将当前标题推入堆栈
                        header: HeaderType = {
                            "level": current_header_level,
                            "name": name,
                            "data": stripped_line[len(sep):].strip(),
                        }
                        header_stack.append(header)
                        # 更新初始元数据
                        initial_metadata[name] = header["data"]

                    # 如果 current_content 不为空，将上一行添加到 lines_with_metadata
                    if current_content:
                        lines_with_metadata.append(
                            {
                                "content": "\n".join(current_content),
                                "metadata": current_metadata.copy(),
                            }
                        )
                        current_content.clear()

                    if not self.strip_headers:
                        current_content.append(stripped_line)

                    break
            else:
                if stripped_line:
                    current_content.append(stripped_line)
                elif current_content:
                    lines_with_metadata.append(
                        {
                            "content": "\n".join(current_content),
                            "metadata": current_metadata.copy(),
                        }
                    )
                    current_content.clear()

            current_metadata = initial_metadata.copy()

        if current_content:
            lines_with_metadata.append(
                {"content": "\n".join(current_content), "metadata": current_metadata}
            )

        # lines_with_metadata 包含每行及其关联的标题元数据
        # 根据共同的元数据聚合这些行
        return self.aggregate_lines_to_chunks(lines_with_metadata,
                                              base_meta=metadata)
