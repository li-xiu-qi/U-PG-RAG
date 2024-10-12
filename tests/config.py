import os

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from rag_config import guiji_api_configs, deepseek_api_configs, zhipu_api_configs
from utils.update_limiter import update_limit

embedding_api_configs = update_limit(guiji_api_configs, 10, 10)
llm_api_configs = guiji_api_configs
rerank_api_configs = update_limit(guiji_api_configs, 10, 10)
from utils import find_project_root_and_load_dotenv

find_project_root_and_load_dotenv("U-PG-RAG")


class ServeConfig:
    ###
    server_host: str = os.getenv("SERVER_HOST")
    model_name: str = os.getenv("MODEL_NAME")
    embedding_model_name: str = os.getenv("EMBEDDING_MODEL_NAME")
    ###
    # pg数据库配置
    db_host: str = os.getenv("DB_HOST")
    db_port: str = os.getenv("DB_PORT")
    db_name: str = os.getenv("DB_NAME")
    default_db_name: str = os.getenv("DEFAULT_DB_NAME")
    db_admin: str = os.getenv("DB_ADMIN")
    db_admin_password: str = os.getenv("DB_ADMIN_PASSWORD")
    db_serve_user: str = os.getenv("DB_SERVE_USER")
    db_serve_user_password: str = os.getenv("DB_SERVE_USER_PASSWORD")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    ACCESS_TOKEN_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    ###
    # 超级管理员账号
    super_admin_account: str = os.getenv("SUPER_ADMIN_ACCOUNT")
    super_admin_password: str = os.getenv("SUPER_ADMIN_PASSWORD")
    super_admin_name: str = os.getenv("SUPER_ADMIN_NAME")
    super_admin_email: str = os.getenv("SUPER_ADMIN_EMAIL")
    ###
    # api_key
    api_key = os.getenv("API_KEY")
    base_url = os.getenv("BASE_URL", None)
    ###
    # rag配置
    embedding_api_configs = embedding_api_configs
    llm_api_configs = llm_api_configs
    rerank_api_configs = rerank_api_configs
    ###
    # minio 配置
    MINIO_DOWNLOAD_URL_EXPIRY = int(os.getenv("DOWNLOAD_URL_EXPIRY", 3600))
    minio_endpoint = os.getenv('MINIO_ENDPOINT', 'localhost:9000')

    minio_access_key = os.getenv('MINIO_ACCESS_KEY')
    minio_secret_key = os.getenv('MINIO_SECRET_KEY')

    minio_region = os.getenv('MINIO_REGION', 'cn-beijing-1')

    minio_file_bucket_name = os.getenv("MINIO_BUCKET_NAME", "file-storage")
    minio_public_images_bucket_name = os.getenv("MINIO_IMAGE_BUCKET_NAME", "public-images")

    ###
    # pg 数据库url
    DATABASE_URL: str = f"postgresql+asyncpg://{db_serve_user}:{db_serve_user_password}@{db_host}:{db_port}/{db_name}"
    NO_ASYNC_DB_URL: str = f"postgresql+psycopg://{db_admin}:{db_admin_password}@{db_host}:{db_port}/{db_name}"
    ADMIN_NO_ASYNC_DB_URL: str = f"postgresql+psycopg://{db_admin}:{db_admin_password}@{db_host}:{db_port}/{default_db_name}"
    ADMIN_NO_ASYNC_NEW_DB_URL: str = f"postgresql+psycopg://{db_admin}:{db_admin_password}@{db_host}:{db_port}/{db_name}"

    ###
    # rag 配置
    chunk_size = 2000
    chunk_overlap = 50
    ###
    # search 配置
    search_engine = os.getenv("SEARCH_ENGINE")
    text_search_url = os.getenv("TEXT_SEARCH_URL")
    news_search_url = os.getenv("NEWS_SEARCH_URL")
    bo_api_key = os.getenv("BO_API_KEY")
    google_api_key = os.getenv("GOOGLE_API_KEY")
    google_cse_id = os.getenv("GOOGLE_CSE_ID")

    ###
    # site filter 目录
    site_filter_path = os.getenv("SITE_FILTER_PATH")
