from uuid import uuid4

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, SQLModel, select

from .auth import get_password_hash
from .config import DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_USERNAME, logger
from .db import engine
from .models import Folder, User
from .router import files, users
from .utils import ensure_storage_exist

app = FastAPI(title="S-Drive Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # TODO change to env var
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(files.router)


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(bind=engine)

    with Session(engine) as session:
        existing = session.exec(
            select(User).where(User.username == DEFAULT_ADMIN_USERNAME)
        ).first()
        if not existing:
            new_user = User(
                username=DEFAULT_ADMIN_USERNAME,
                hashed_password=get_password_hash(DEFAULT_ADMIN_PASSWORD),
                is_admin=True,
            )
            folder = Folder(
                folder_name=new_user.username,
                owner_id=new_user.id,
            )
            ensure_storage_exist(user=new_user, folder=folder)
            new_user.top_folder_id = folder.id
            session.add(new_user)
            session.add(folder)
            session.commit()
            session.refresh(new_user)
            logger.info("USER CREATED: %s", new_user.username)


@app.get("/")
def root():
    """
    s-drive-server
    """
    return {"s-drive-server": "running :)"}
