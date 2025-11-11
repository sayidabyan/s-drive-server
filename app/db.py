from sqlmodel import Session, create_engine

from .config import DB_URL

connect_args = {"check_same_thread": False}
engine = create_engine(DB_URL, echo=True, connect_args=connect_args)


def get_session():
    with Session(engine) as session:
        yield session
