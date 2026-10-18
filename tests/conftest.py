from pathlib import Path

import pytest
from sqlalchemy.orm import Session

import core.qa.models  # noqa: F401  (registra as tabelas em Base.metadata)
from core.database import Base, get_engine
from core.qa.enums import Papel, Severidade
from core.qa.repositories import bugs, membros

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


@pytest.fixture
def novo_membro(sessao):
    def _criar(nome="Ana", papel=Papel.DEV):
        return membros.criar_membro(sessao, nome, papel)

    return _criar


@pytest.fixture
def novo_bug(sessao):
    def _criar(**extras):
        dados = {"titulo": "Erro no login", "severidade": Severidade.ALTA, "modulo": "Login"}
        dados.update(extras)
        return bugs.criar_bug(sessao, **dados)

    return _criar
