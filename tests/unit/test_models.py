import pytest
from sqlalchemy.orm import Session

from core.database import Base, get_engine
from core.models import Bug, Severidade, Status


@pytest.fixture
def sessao():
    engine = get_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


def test_bug_novo_recebe_valores_padrao(sessao):
    bug = Bug(
        titulo="Botão salvar não responde",
        severidade=Severidade.ALTA,
        modulo="Cadastro",
    )
    sessao.add(bug)
    sessao.commit()

    salvo = sessao.get(Bug, bug.id)
    assert salvo.status == Status.ABERTO
    assert salvo.aberto_em is not None
    assert salvo.resolvido_em is None
    assert salvo.responsavel is None
