# 从  https://github.com/InternLM/HuixiangDou 修改而来


from dataclasses import dataclass, field
from typing import (Dict, TypedDict)


@dataclass
class Chunk:
    content_or_path: str = ''  # 文本内容或路径
    metadata: dict = field(default_factory=dict)  # 元数据字典
    modal: str = 'text'  # 模态类型，可以是 'text', 'image', 'audio' 之一

    def __post_init__(self):
        if self.modal not in ['text', 'image', 'audio']:
            raise ValueError(
                f'无效的模态: {self.modal}。允许的值为: `text`, `image`, `audio`'
            )

    def __str__(self) -> str:
        """重写 __str__ 方法，仅包含 content_or_path 和 metadata。

        该格式匹配 pydantic 的 __str__ 格式。

        这样做的目的是确保用户代码直接将 Document 对象传递到提示中时不会因添加 id 字段（或将来添加的任何其他字段）而发生变化。

        该重写可能会在将来被移除，取而代之的是在提示中直接格式化内容的更通用解决方案。
        """
        if self.metadata:
            return f"modal='{self.modal}' content_or_path='{self.content_or_path}' metadata={self.metadata}"
        else:
            return f"modal='{self.modal}' content_or_path='{self.content_or_path}'"

    def __repr__(self) -> str:
        return self.__str__()


class LineType(TypedDict):
    """行类型，使用 TypedDict 定义。"""

    metadata: Dict[str, str]
    content: str


class HeaderType(TypedDict):
    """头部类型，使用 TypedDict 定义。"""

    level: int
    name: str
    data: str
