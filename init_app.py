import logging

from app.core.init_func import init_rag, \
    init_db


def init_app(reset_db: bool = True):
    """整合了数据库初始化，RAG模型初始化，MinIO客户端初始化的函数"""
    init_db(reset_db)
    init_rag()
    logging.info("Application initialized successfully.")






