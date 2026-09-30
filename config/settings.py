import os
import shutil
import sys
from pathlib import Path

from dotenv import load_dotenv


def get_env_path() -> Path:
    if getattr(sys, "frozen", False):
        return (
            Path(sys.executable).resolve().parent
            / ".env"
        )

    return (
        Path(__file__).resolve().parents[1]
        / ".env"
    )


load_dotenv(
    dotenv_path=get_env_path()
)


APP_DATA_DIR = Path.home() / ".fileforge"
DB_PATH = APP_DATA_DIR / "fileforge.db"
LOG_DIR = APP_DATA_DIR / "logs"

LEGACY_DB_PATH = Path.home() / ".eva" / "eva.db"


def ensure_app_data() -> None:
    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not DB_PATH.exists() and LEGACY_DB_PATH.exists():
        shutil.copy2(LEGACY_DB_PATH, DB_PATH)


FILEFORGE_DATABASE_URL = os.getenv(
    "FILEFORGE_DATABASE_URL"
)