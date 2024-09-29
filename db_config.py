from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

from config import ServeConfig

Base = declarative_base()
no_async_engine = create_engine(ServeConfig.NO_ASYNC_DB_URL)
