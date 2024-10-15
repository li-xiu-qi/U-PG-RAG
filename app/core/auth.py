from datetime import datetime, timedelta
from typing import Type, Optional, Tuple
from fastapi import HTTPException, status
from jose import jwt, JWTError, ExpiredSignatureError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import ServeConfig
from app.schemes.models.user_models import ResponseAdmin


async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> Tuple[str, datetime]:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ServeConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, ServeConfig.SECRET_KEY, algorithm=ServeConfig.ALGORITHM)
    return encoded_jwt, expire


async def get_admin_user(current_user: ResponseAdmin):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


async def authenticate_user(*, db: AsyncSession, dbmodel: Type["User"], account: str, password: str):
    query = select(dbmodel).filter_by(account=account)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not ServeConfig.pwd_context.verify(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def decode_and_validate_token(token: str, client_ip: str, required_scope: str) -> dict:
    try:
        payload = jwt.decode(token, ServeConfig.SECRET_KEY, algorithms=[ServeConfig.ALGORITHM])
        validate_token_payload(payload, client_ip, required_scope)
    except ExpiredSignatureError:
        payload = jwt.decode(token, ServeConfig.SECRET_KEY, algorithms=[ServeConfig.ALGORITHM],
                             options={"verify_exp": False})
        validate_token_payload(payload, client_ip, required_scope)
    except JWTError:
        raise get_credentials_exception()
    return payload


def validate_token_payload(payload: dict, client_ip: str, required_scope: str):
    user_account: str = payload.get("sub")
    token_ip: str = payload.get("ip")
    token_scope: str = payload.get("scope")
    if user_account is None or token_ip != client_ip or required_scope not in token_scope.split():
        raise get_credentials_exception()


def get_credentials_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )