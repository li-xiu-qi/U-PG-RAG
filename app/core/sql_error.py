import json
import os
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.log_config import setup_logger

logger = setup_logger(__name__, "logs/error_handling.log", "error")

ERROR_RECORD_FILE = 'error_record.json'


def save_unique_error(error_message: str):
    if os.path.exists(ERROR_RECORD_FILE):
        with open(ERROR_RECORD_FILE, 'r') as file:
            error_records = json.load(file)
    else:
        error_records = []

    if error_message not in error_records:
        error_records.append(error_message)
        with open(ERROR_RECORD_FILE, 'w') as file:
            json.dump(error_records, file, indent=2, ensure_ascii=False)


def handle_sqlalchemy_error(status_code: int = 500, detail: str = "A database error occurred"):
    def decorator(func: Callable):
        async def wrapper(*, session: AsyncSession, **kwargs):
            try:
                return await func(session=session, **kwargs)
            except SQLAlchemyError as e:
                error_message = f"{type(e).__name__} occurred: {e}"
                save_unique_error(error_message)
                logger.error(error_message)
                raise HTTPException(status_code=status_code, detail=detail)
            except Exception as e:
                error_message = f"Unexpected error occurred: {e}"
                save_unique_error(error_message)
                logger.error(error_message)
                raise HTTPException(status_code=500, detail="An unexpected error occurred.")

        return wrapper

    return decorator
