import os


def get_project_root(project_name: str, stop_dir: str | None = None, start_dir: str | None = None, ) -> str:
    """
    根据项目名称获取项目的根目录绝对路径。

    :param start_dir: 起始目录，如果为 None 则使用 __file__
    :param project_name: 项目的名字
    :param stop_dir: 终止文件夹名
    :return: 项目根目录的绝对路径
    """
    if start_dir is None:
        start_dir = os.path.dirname(__file__)

    # 获取当前操作系统使用的路径分隔符
    path_separator = os.sep

    current_dir = start_dir

    parts = current_dir.split(path_separator)

    while parts:
        candidate = os.path.join(*parts)
        if os.path.basename(candidate) == project_name:
            return candidate
        if stop_dir and os.path.basename(candidate) == stop_dir:
            break

        # 移除最后一个部分，向上一级目录移动
        parts.pop()

    raise RuntimeError(f"Project '{project_name}' not found.")


if __name__ == "__main__":
    print(get_project_root("U-PG-RAG", "U-PG-RAG"))
