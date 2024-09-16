import sqlalchemy
from sqlalchemy import create_engine, Connection

from app.serves.model_serves import RAG
from app.serves.model_serves.client_manager import ClientManager
from config import ServeConfig
from rag_config import embedding_api_configs, llm_api_configs


def init_db():
    _create_database_and_user()
    _create_extensions_in_new_db()
    init_rag()


def _create_extensions(conn: Connection, extensions: list) -> None:
    for extension in extensions:
        statement = sqlalchemy.text(f"CREATE EXTENSION IF NOT EXISTS {extension};")
        conn.execute(statement)
    conn.commit()


def _create_database_and_user():
    admin_engine = create_engine(ServeConfig.ADMIN_NO_ASYNC_DB_URL)
    with admin_engine.connect() as conn:
        conn.execute(sqlalchemy.text("COMMIT"))

        database_exists = conn.execute(
            sqlalchemy.text(f"SELECT 1 FROM pg_database WHERE datname = '{ServeConfig.db_name}'")).first()

        if not database_exists:
            conn.execute(
                sqlalchemy.text(
                    f"CREATE DATABASE {ServeConfig.db_name} ENCODING 'UTF8' LC_COLLATE='zh_CN.UTF-8' LC_CTYPE='zh_CN.UTF-8'"))

        user_exists = conn.execute(
            sqlalchemy.text(f"SELECT 1 FROM pg_roles WHERE rolname = '{ServeConfig.db_serve_user}'")).first()

        if not user_exists:
            conn.execute(
                sqlalchemy.text(
                    f"CREATE USER {ServeConfig.db_serve_user} WITH PASSWORD '{ServeConfig.db_serve_user_password}'"))

        new_db_engine = create_engine(ServeConfig.ADMIN_NO_ASYNC_NEW_DB_URL)
        with new_db_engine.connect() as new_conn:
            new_conn.execute(sqlalchemy.text(
                f"GRANT ALL PRIVILEGES ON DATABASE {ServeConfig.db_name} TO {ServeConfig.db_serve_user}"))


def _create_extensions_in_new_db():
    new_engine = create_engine(ServeConfig.ADMIN_NO_ASYNC_NEW_DB_URL)
    with new_engine.connect() as conn:
        _create_extensions(conn, ["vector", "pg_jieba"])


rag_embedding: RAG | None = None
rag_chat: RAG | None = None


def init_rag():
    global rag_embedding, rag_chat
    embedding_client = ClientManager(api_configs=embedding_api_configs)
    chat_client = ClientManager(api_configs=llm_api_configs)
    rag_embedding = RAG(client_manager=embedding_client)
    rag_chat = RAG(client_manager=chat_client)
