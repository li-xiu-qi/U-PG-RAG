import logging

from diskcache import Cache
from sqlalchemy import create_engine, text, Connection
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from app.crud.file_utils.minio_service import MinIOFileService, init_minio_client
from app.db import db_models
from app.serves.model_serves.chat_model import ChatModel
from app.serves.model_serves.client_manager import ClientManager
from app.serves.model_serves.embedding_model import EmbeddingModel
from app.serves.model_serves.rerank_model import RerankModel
from config import ServeConfig
from db_config import Base, no_async_engine
from model_constant import set_embedding_model, set_chat_model, set_rerank_model


def initialize_super_admin(session: Session):
    """初始化超级管理员账号"""
    try:
        query = select(db_models.User).filter_by(account=ServeConfig.super_admin_account, role="super_admin")
        super_admin = session.execute(query).scalar_one_or_none()

        if super_admin:
            logging.info("Deleting existing super admin user.")
            session.delete(super_admin)
            session.commit()

        # 创建新的超级管理员
        hashed_password = ServeConfig.pwd_context.hash(ServeConfig.super_admin_password)
        new_super_admin = db_models.User(
            account=ServeConfig.super_admin_account,
            hashed_password=hashed_password,
            name=ServeConfig.super_admin_name,
            email=ServeConfig.super_admin_email,
            phone="12345678901",
            status=True,
            role="super_admin"
        )
        session.add(new_super_admin)
        session.commit()
        session.refresh(new_super_admin)

        logging.info("New super admin created successfully.")
    except Exception as e:
        session.rollback()
        logging.error(f"Error initializing super admin: {e}")
        raise


def create_database_and_user():
    """创建数据库和用户"""
    try:
        with create_engine(ServeConfig.ADMIN_NO_ASYNC_DB_URL).connect() as conn:
            conn.execute(text("COMMIT"))

            # 检查数据库是否存在
            db_exists = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{ServeConfig.db_name}'")).first()
            if not db_exists:
                conn.execute(text(
                    f"CREATE DATABASE {ServeConfig.db_name} ENCODING 'UTF8' "
                    f"LC_COLLATE='zh_CN.UTF-8' LC_CTYPE='zh_CN.UTF-8'"))
                logging.info(f"Database '{ServeConfig.db_name}' created successfully.")
            else:
                logging.info(f"Database '{ServeConfig.db_name}' already exists.")

            # 检查用户是否存在
            user_exists = conn.execute(
                text(f"SELECT 1 FROM pg_roles WHERE rolname = '{ServeConfig.db_serve_user}'")).first()
            if not user_exists:
                conn.execute(text(
                    f"CREATE USER {ServeConfig.db_serve_user} WITH PASSWORD '{ServeConfig.db_serve_user_password}'"))
                logging.info(f"User '{ServeConfig.db_serve_user}' created successfully.")
            else:
                logging.info(f"User '{ServeConfig.db_serve_user}' already exists.")
            conn.execute(text("COMMIT"))

            # 为新数据库赋予权限
            with create_engine(ServeConfig.ADMIN_NO_ASYNC_NEW_DB_URL).connect() as new_conn:
                new_conn.execute(text(
                    f"GRANT ALL PRIVILEGES ON DATABASE {ServeConfig.db_name} TO {ServeConfig.db_serve_user}"))
                logging.info(
                    f"Granted privileges on database '{ServeConfig.db_name}' to user '{ServeConfig.db_serve_user}'.")
                new_conn.execute(text("COMMIT"))

    except Exception as e:
        logging.error(f"Error creating database and user: {e}")
        raise


def create_extensions(conn: Connection, extensions: list):
    """在数据库中创建扩展"""
    try:
        for extension in extensions:
            conn.execute(text(f"CREATE EXTENSION IF NOT EXISTS {extension};"))
        conn.commit()
        logging.info(f"Extensions {extensions} created successfully.")
    except Exception as e:
        conn.rollback()
        logging.error(f"Error creating extensions: {e}")
        raise


def setup_database(reset_db: bool = False):
    """设置数据库，创建表，初始化MinIO客户端，并赋予权限"""
    new_db_engine = create_engine(ServeConfig.ADMIN_NO_ASYNC_NEW_DB_URL)
    if reset_db:
        logging.info("Dropping all tables...")
        with new_db_engine.connect() as conn:
            Base.metadata.drop_all(bind=new_db_engine)
            conn.commit()

    logging.info("Creating all tables...")
    Base.metadata.create_all(bind=new_db_engine)
    with new_db_engine.connect() as conn:
        try:
            conn.commit()

            result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
            tables = result.fetchall()
            logging.info(f"Existing tables: {[table[0] for table in tables]}")

            minio_client = init_minio_client()
            MinIOFileService(minio_client, ServeConfig.minio_file_bucket_name)
            logging.info("MinIO client initialized successfully.")

            logging.info(f"Granting privileges to user {ServeConfig.db_serve_user}.")
            conn.execute(text(f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {ServeConfig.db_serve_user}"))
            conn.execute(text(f"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {ServeConfig.db_serve_user}"))

            conn.commit()

            logging.info("Database setup completed successfully.")
        except Exception as e:
            conn.rollback()
            logging.error(f"Error during database setup: {e}")
            raise


def init_db(reset_db: bool = False):
    """初始化数据库，包括创建数据库和用户，扩展模块，以及超级管理员"""
    try:
        create_database_and_user()

        with create_engine(ServeConfig.ADMIN_NO_ASYNC_NEW_DB_URL).connect() as conn:
            create_extensions(conn, ["vector", "pg_jieba"])

        # 设置数据库并初始化超级管理员
        setup_database(reset_db)
        with Session(no_async_engine) as session:
            initialize_super_admin(session)
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        raise


def init_rag():
    """初始化RAG模型的客户端管理器"""
    try:
        embedding_cache = Cache("./embedding_cache")
        embedding_client = ClientManager(api_configs=ServeConfig.embedding_api_configs)
        chat_client = ClientManager(api_configs=ServeConfig.llm_api_configs)
        rerank_client = ClientManager(api_configs=ServeConfig.rerank_api_configs)

        embedding_model = EmbeddingModel(client_manager=embedding_client, cache=embedding_cache)
        chat_model = ChatModel(client_manager=chat_client)
        rerank_model = RerankModel(client_manager=rerank_client)

        set_embedding_model(embedding_model)
        set_chat_model(chat_model)
        set_rerank_model(rerank_model)
        logging.info("RAG model initialized successfully.")
    except Exception as e:
        logging.error(f"Error initializing RAG model: {e}")
        raise
