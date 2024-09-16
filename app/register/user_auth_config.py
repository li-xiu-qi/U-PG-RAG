from fastapi import HTTPException, status
from jose import jwt, JWTError, ExpiredSignatureError

from config import ServeConfig


def decode_and_validate_token(token: str, client_ip: str) -> dict:
    try:
        payload = jwt.decode(token, ServeConfig.SECRET_KEY, algorithms=[ServeConfig.ALGORITHM])
        username: str = payload.get("sub")
        token_ip: str = payload.get("ip")
        if username is None or token_ip != client_ip:
            raise get_credentials_exception()
    except ExpiredSignatureError:
        payload = jwt.decode(token, ServeConfig.SECRET_KEY, algorithms=[ServeConfig.ALGORITHM],
                             options={"verify_exp": False})
        username: str = payload.get("sub")
        token_ip: str = payload.get("ip")
        if username is None or token_ip != client_ip:
            raise get_credentials_exception()
    except JWTError:
        raise get_credentials_exception()
    return payload


def get_credentials_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
