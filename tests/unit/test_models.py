import pytest
from sqlalchemy.exc import IntegrityError

from core.qa.enums import Papel, Severidade, Status
from core.qa.models import Bug, Membro


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
    assert salvo.responsavel_id is None


def test_bug_pode_ter_responsavel(sessao):
    membro = Membro(nome="Ana", papel=Papel.DEV)
    sessao.add(membro)
    sessao.commit()

    bug = Bug(
        titulo="Erro no login",
        severidade=Severidade.MEDIA,
        modulo="Login",
        responsavel_id=membro.id,
    )
    sessao.add(bug)
    sessao.commit()

    assert bug.responsavel is not None
    assert bug.responsavel.nome == "Ana"


def test_banco_rejeita_responsavel_inexistente(sessao):
    sessao.add(
        Bug(
            titulo="Erro no login",
            severidade=Severidade.BAIXA,
            modulo="Login",
            responsavel_id=999,
        )
    )
    with pytest.raises(IntegrityError):
        sessao.commit()
