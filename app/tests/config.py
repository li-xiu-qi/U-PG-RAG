import os
from utils import find_project_root_and_load_dotenv

find_project_root_and_load_dotenv("U-PG-RAG")


class ServeConfig:
    db_host: str = os.getenv("DB_HOST")
    db_port: str = os.getenv("DB_PORT")
    db_name: str = os.getenv("DB_NAME")
    default_db_name: str = os.getenv("DEFAULT_DB_NAME")
    db_admin: str = os.getenv("DB_ADMIN")
    db_admin_password: str = os.getenv("DB_ADMIN_PASSWORD")
    db_serve_user: str = os.getenv("DB_SERVE_USER")
    db_serve_user_password: str = os.getenv("DB_SERVE_USER_PASSWORD")

    super_admin_account: str = os.getenv("SUPER_ADMIN_ACCOUNT")
    super_admin_password: str = os.getenv("SUPER_ADMIN_PASSWORD")
    super_admin_name: str = os.getenv("SUPER_ADMIN_NAME")
    super_admin_email: str = os.getenv("SUPER_ADMIN_EMAIL")

    DATABASE_URL: str = f"postgresql+asyncpg://{db_serve_user}:{db_serve_user_password}@{db_host}:{db_port}/{db_name}"
    NO_ASYNC_DB_URL: str = f"postgresql+psycopg2://{db_admin}:{db_admin_password}@{db_host}:{db_port}/{db_name}"
    ADMIN_NO_ASYNC_DB_URL: str = f"postgresql+psycopg2://{db_admin}:{db_admin_password}@{db_host}:{db_port}/{default_db_name}"
    ADMIN_NO_ASYNC_NEW_DB_URL: str = f"postgresql+psycopg2://{db_admin}:{db_admin_password}@{db_host}:{db_port}/{db_name}"

    api_key = os.getenv("API_KEY")
    base_url = os.getenv("BASE_URL", None)
