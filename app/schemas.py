from typing import Optional
from uuid import UUID

from sqlmodel import SQLModel

from .models import File, Folder


class Token(SQLModel):
    access_token: str
    token_type: str


class UserResponse(SQLModel):
    id: UUID
    username: str
    is_admin: bool
    top_folder_id: Optional[UUID]


class UserCreate(SQLModel):
    username: str
    password: str
    is_admin: bool


class ChildFolderResponse(SQLModel):
    id: UUID
    folder_name: str
    parent_id: Optional[UUID]
    owner_id: UUID


class FolderChildrenResponse(SQLModel):
    id: UUID
    folder_name: str
    parent_id: Optional[UUID]
    owner_id: UUID
    child_folders: list[ChildFolderResponse]
    files: list[File]


class FolderCreate(SQLModel):
    folder_name: str
    parent_id: Optional[UUID] = None
