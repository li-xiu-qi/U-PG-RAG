import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

from utils import find_project_root_and_load_dotenv

find_project_root_and_load_dotenv("U-PG-RAG")

DATABASE_URL = os.getenv("DATABASE_URL")
NO_ASYNC_DB_URL = os.getenv("NO_ASYNC_DB_URL")
admin_conn_info = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
}

Base = declarative_base()

engine = create_engine(NO_ASYNC_DB_URL)
