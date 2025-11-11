import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


STORAGE_ROOT_STR = os.getenv("STORAGE_ROOT", "./data")
STORAGE_ROOT = Path(os.getenv("STORAGE_ROOT", "./data")).resolve()
STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
DB_URL = os.getenv("DB_URL", "sqlite:///database.db")
JWT_SECRET_KEY = os.getenv("SECRET_KEY", "default-s-drive-sk")
JWT_ACCESS_TOKEN_DURATION = os.getenv("ACCESS_TOKEN_DURATION", 60)
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
DEFAULT_ADMIN_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
