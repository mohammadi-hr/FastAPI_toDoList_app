from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    expire = datetime.now() + \
        (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = data.copy()

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
