from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from .db import engine
from .models import File, Folder, User


def get_user_by_username(username: str):
    with Session(engine) as session:
        return session.exec(select(User).where(User.username == username)).first()


def get_owned_folder(user: User, folder_id: UUID, session: Session) -> Folder:
    folder = session.exec(
        select(Folder)
        .options(selectinload(Folder.child_folders))
        .where(Folder.id == folder_id)
    ).first()
    if not folder or folder.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Folder not found")
    return folder


def get_owned_file(user: User, file_id: UUID, session: Session) -> Folder:
    file = session.exec(select(File).where(File.id == file_id)).first()
    if not file or file.owner_id != user.id:
        raise HTTPException(status_code=404, detail="File not found")
    return file
