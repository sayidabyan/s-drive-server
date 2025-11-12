from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from ..auth import (
    authenticate_user,
    create_access_token,
    get_admin_status,
    get_current_user,
    get_password_hash,
)
from ..config import logger
from ..db import get_session
from ..models import Folder, User
from ..schemas import Token, UserCreate, UserResponse
from ..utils import ensure_storage_exist

router = APIRouter()


@router.post("/token")
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    Receive username and password and return jwt token
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")


@router.get("/get_current_user", response_model=UserResponse)
def read_current_user(user: User = Depends(get_current_user)):
    """
    Return User data according to the access_token received
    """
    return user


@router.post("/create-user", response_model=UserResponse)
def create_user(
    user: UserCreate,
    session: Session = Depends(get_session),
    authorized: bool = Depends(get_admin_status),
):
    """
    Receive username and password and return the created User object
    """
    existing = session.exec(select(User).where(User.username == user.username)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already exists"
        )
    new_user = User(
        username=user.username,
        hashed_password=get_password_hash(user.password),
        is_admin=user.is_admin,
    )
    folder = Folder(
        folder_name=user.username,
        owner_id=new_user.id,
    )
    ensure_storage_exist(user=new_user, folder=folder)
    new_user.top_folder_id = folder.id
    session.add(new_user)
    session.add(folder)
    session.commit()
    session.refresh(new_user)
    logger.info("USER CREATED: %s", new_user.username)
    return new_user


@router.delete("/delete-user/{user_id}", response_model=UserResponse)
def delete_user(
    user_id: UUID,
    session: Session = Depends(get_session),
    authorized: bool = Depends(get_admin_status),
):
    """
    Receive user_id and return the deleted User object
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User doesn't exist"
        )
    session.delete(user)
    session.commit()
    return user


@router.get("/list-user", response_model=list[UserResponse])
def get_list_users(
    session: Session = Depends(get_session),
    authorized: bool = Depends(get_admin_status),
):
    """
    Receive user_id and return list of all User
    """
    return session.exec(select(User)).all()
