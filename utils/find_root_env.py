import os

from dotenv import load_dotenv


def find_project_root_and_load_dotenv(project_name):
    """
    根据项目名称查找项目根目录，并加载该目录下的 .env 文件。

    :param project_name: 项目名称
    """
    current_dir = os.path.abspath(os.getcwd())

    while True:
        if os.path.basename(current_dir) == project_name:
            env_path = os.path.join(current_dir, '.env')
            if os.path.exists(env_path):
                load_dotenv(dotenv_path=env_path)
                print(f"Loaded .env file from: {env_path}")
                return
            else:
                print(f"No .env file found in project directory: {current_dir}")
                return
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            print(f"Project directory '{project_name}' not found")
            return
        current_dir = parent_dir
