import os


def get_project_root(project_name: str) -> str:
    """
    根据项目名称获取项目的根目录绝对路径。

    :param project_name: 项目的名字
    :return: 项目根目录的绝对路径
    """
    # 获取当前操作系统使用的路径分隔符
    path_separator = os.sep

    current_dir = os.path.dirname(__file__)

    # 分割路径
    parts = current_dir.split(path_separator)

    while parts:
        candidate = os.path.join(*parts)
        if os.path.basename(candidate) == project_name:
            return candidate

        # 移除最后一个部分，向上一级目录移动
        parts.pop()

    raise RuntimeError(f"Project '{project_name}' not found.")
