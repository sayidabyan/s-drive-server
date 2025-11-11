import uuid
from pathlib import Path
from typing import Optional

from sqlmodel import Session, select

from .auth import get_password_hash
from .config import STORAGE_ROOT
from .db import engine
from .models import Folder, User


def sanitize_filename(name: str) -> str:
    """
    Sanitize filename in order to prevent traversal
    """
    return Path(name).name


def ensure_storage_exist(user: User, folder: Folder):
    path = STORAGE_ROOT / str(user.id) / str(folder.id)
    path.mkdir(parents=True, exist_ok=True)
    return path
