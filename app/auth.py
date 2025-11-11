from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from sqlmodel import Session, select

from .config import JWT_ACCESS_TOKEN_DURATION, JWT_ALGORITHM, JWT_SECRET_KEY
from .db import get_session
from .models import User
from .query import get_user_by_username

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

credentials_invalid_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
credentials_expired_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token expired",
    headers={"WWW-Authenticate": "Bearer"},
)
credentials_unauthorized_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Action not authorized",
    headers={"WWW-Authenticate": "Bearer"},
)


def authenticate_user(username, password) -> Optional[User]:
    user = get_user_by_username(username)
    if user:
        if verify_password(password, user.hashed_password):
            return user
    return None


def verify_password(plain_password: str, hashed_password) -> str:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_DURATION)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username = payload.get("sub")
        expire = payload.get("exp")
        if username is None:
            raise credentials_invalid_exception_exception
        if expire is None:
            raise credentials_invalid_exception_exception
    except InvalidTokenError:
        raise credentials_invalid_exception

    user = get_user_by_username(username=username)
    if user is None:
        raise credentials_invalid_exception
    return user


def get_admin_status(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise credentials_unauthorized_exception
    return user.is_admin
