import logging

import sqlalchemy
from minio import Minio
from sqlalchemy import Connection, create_engine
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from app.apis.db_config import Base, no_async_engine
from config import ServeConfig
from app.crud.file_utils.minio_service import MinIOFileService
from app.db import db_models


def setup_database(reset_db: bool = False):
    new_db_engine = create_engine(ServeConfig.ADMIN_NO_ASYNC_NEW_DB_URL)

    try:
        if reset_db:
            Base.metadata.drop_all(bind=new_db_engine)

        Base.metadata.create_all(bind=new_db_engine)

        with new_db_engine.connect() as new_conn:
            new_conn.execute(
                sqlalchemy.text(f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {ServeConfig.db_serve_user}"))
            new_conn.execute(
                sqlalchemy.text(
                    f"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {ServeConfig.db_serve_user}"))

        initialize_super_admin()
        minio_client = init_minio_client()
        MinIOFileService(minio_client, ServeConfig.minio_bucket_name)
    except Exception as e:
        logging.error(f"Error during database setup: {e}")
        raise


def initialize_super_admin():
    with Session(no_async_engine) as session:
        query = select(db_models.User).filter_by(account=ServeConfig.super_admin_account, role="super_admin")
        result = session.execute(query)
        super_admin = result.scalar_one_or_none()
        if super_admin:
            logging.info("Deleting existing super admin user.")
            session.delete(super_admin)
            session.commit()

        hashed_password = ServeConfig.pwd_context.hash(ServeConfig.super_admin_password)
        super_admin = db_models.User(
            account=ServeConfig.super_admin_account,
            hashed_password=hashed_password,
            name=ServeConfig.super_admin_name,
            email=ServeConfig.super_admin_email,
            phone="12345678901",
            status=True,
            role="super_admin"
        )
        logging.info("Creating new super admin user.")
        session.add(super_admin)
        session.commit()
        session.refresh(super_admin)


def init_minio_client():
    minio_client = Minio(
        ServeConfig.minio_endpoint,
        access_key=ServeConfig.minio_access_key,
        secret_key=ServeConfig.minio_secret_key,
        secure=False,
        region=ServeConfig.minio_region
    )
    return minio_client


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Setup the database.")
    parser.add_argument("--reset-db", action="store_true", help="Reset the database schema.")
    args = parser.parse_args()

    setup_database(reset_db=args.reset_db)
