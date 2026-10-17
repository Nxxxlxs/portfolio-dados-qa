from pathlib import Path

import pytest
from sqlalchemy.orm import Session

import core.models  # noqa: F401  (registra as tabelas em Base.metadata)
from core.database import Base, get_engine

RAIZ = Path(__file__).resolve().parents[1]


@pytest.fixture
def sessao():
    engine = get_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


@pytest.fixture
def app_main() -> str:
    return str(RAIZ / "app" / "main.py")
