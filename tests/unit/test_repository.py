from datetime import date

import pytest

from core import repository as repo
from core.models import Severidade, Status


def _novo_bug(sessao, **extras):
    dados = {"titulo": "Erro no login", "severidade": Severidade.ALTA, "modulo": "Login"}
    dados.update(extras)
    return repo.criar_bug(sessao, **dados)


def test_criar_e_obter_bug(sessao):
    bug = _novo_bug(sessao)

    encontrado = repo.obter_bug(sessao, bug.id)
    assert encontrado is not None
    assert encontrado.titulo == "Erro no login"
    assert encontrado.status == Status.ABERTO


def test_listar_filtra_por_status_e_modulo(sessao):
    _novo_bug(sessao, modulo="Login")
    corrigido = _novo_bug(sessao, modulo="Checkout")
    repo.atualizar_bug(sessao, corrigido.id, status=Status.CORRIGIDO)

    assert len(repo.listar_bugs(sessao)) == 2
    assert len(repo.listar_bugs(sessao, status=Status.ABERTO)) == 1
    assert repo.listar_bugs(sessao, modulo="Checkout")[0].id == corrigido.id


def test_corrigir_bug_preenche_data_de_resolucao(sessao):
    bug = _novo_bug(sessao)

    atualizado = repo.atualizar_bug(sessao, bug.id, status=Status.CORRIGIDO)

    assert atualizado is not None
    assert atualizado.resolvido_em == date.today()


def test_reabrir_bug_limpa_data_de_resolucao(sessao):
    bug = _novo_bug(sessao)
    repo.atualizar_bug(sessao, bug.id, status=Status.FECHADO)

    reaberto = repo.atualizar_bug(sessao, bug.id, status=Status.REABERTO)

    assert reaberto is not None
    assert reaberto.resolvido_em is None


def test_atualizar_campo_invalido_levanta_erro(sessao):
    bug = _novo_bug(sessao)

    with pytest.raises(ValueError, match="não editáveis"):
        repo.atualizar_bug(sessao, bug.id, id=999)


def test_atualizar_bug_inexistente_retorna_none(sessao):
    assert repo.atualizar_bug(sessao, 999, titulo="Novo título") is None


def test_excluir_bug(sessao):
    bug = _novo_bug(sessao)

    assert repo.excluir_bug(sessao, bug.id) is True
    assert repo.obter_bug(sessao, bug.id) is None
    assert repo.excluir_bug(sessao, bug.id) is False
