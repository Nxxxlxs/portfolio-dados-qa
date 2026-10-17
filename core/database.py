from pathlib import Path

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DB_URL = f"sqlite:///{DATA_DIR / 'portfolio.db'}"


class Base(DeclarativeBase):
    """Classe base de todos os modelos."""


def get_engine(url: str = DB_URL) -> Engine:
    if ":memory:" not in url:
        DATA_DIR.mkdir(exist_ok=True)
    return create_engine(url)
