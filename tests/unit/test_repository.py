from datetime import date

import pytest

from core import repository as repo
from core.qa.enums import Papel, Severidade, Status


def _novo_membro(sessao, nome="Ana", papel=Papel.DEV):
    return repo.criar_membro(sessao, nome, papel)


def _novo_bug(sessao, **extras):
    dados = {"titulo": "Erro no login", "severidade": Severidade.ALTA, "modulo": "Login"}
    dados.update(extras)
    return repo.criar_bug(sessao, **dados)


# ---------- Membros ----------


def test_criar_membro_nasce_ativo(sessao):
    membro = _novo_membro(sessao, "  Ana  ")

    assert membro.nome == "Ana"
    assert membro.ativo is True


def test_criar_membro_sem_nome_levanta_erro(sessao):
    with pytest.raises(ValueError, match="obrigatório"):
        _novo_membro(sessao, "   ")


def test_criar_membro_com_nome_repetido_levanta_erro(sessao):
    _novo_membro(sessao, "Ana")

    with pytest.raises(ValueError, match="Já existe"):
        _novo_membro(sessao, " ana ")


def test_listar_membros_filtra_por_papel_e_ativos(sessao):
    ana = _novo_membro(sessao, "Ana", Papel.DEV)
    _novo_membro(sessao, "Bruno", Papel.QA)
    repo.definir_ativo(sessao, ana.id, False)

    assert [m.nome for m in repo.listar_membros(sessao)] == ["Bruno"]
    assert len(repo.listar_membros(sessao, somente_ativos=False)) == 2
    assert repo.listar_membros(sessao, papel=Papel.DEV) == []


def test_definir_ativo_de_membro_inexistente_retorna_none(sessao):
    assert repo.definir_ativo(sessao, 999, False) is None


# ---------- Bugs ----------


def test_criar_e_obter_bug(sessao):
    bug = _novo_bug(sessao)

    encontrado = repo.obter_bug(sessao, bug.id)
    assert encontrado is not None
    assert encontrado.titulo == "Erro no login"
    assert encontrado.status == Status.ABERTO


def test_criar_bug_com_responsavel(sessao):
    membro = _novo_membro(sessao)

    bug = _novo_bug(sessao, responsavel_id=membro.id)

    assert bug.responsavel is not None
    assert bug.responsavel.nome == "Ana"


def test_criar_bug_com_responsavel_inexistente_levanta_erro(sessao):
    with pytest.raises(ValueError, match="não encontrado"):
        _novo_bug(sessao, responsavel_id=999)


def test_criar_bug_com_responsavel_inativo_levanta_erro(sessao):
    membro = _novo_membro(sessao)
    repo.definir_ativo(sessao, membro.id, False)

    with pytest.raises(ValueError, match="inativo"):
        _novo_bug(sessao, responsavel_id=membro.id)


def test_desativar_membro_mantem_o_historico_dos_bugs(sessao):
    membro = _novo_membro(sessao)
    bug = _novo_bug(sessao, responsavel_id=membro.id)

    repo.definir_ativo(sessao, membro.id, False)

    salvo = repo.obter_bug(sessao, bug.id)
    assert salvo is not None
    assert salvo.responsavel_id == membro.id
    assert salvo.responsavel is not None
    assert salvo.responsavel.nome == "Ana"


def test_listar_filtra_por_status_modulo_e_responsavel(sessao):
    ana = _novo_membro(sessao)
    _novo_bug(sessao, modulo="Login")
    corrigido = _novo_bug(sessao, modulo="Checkout", responsavel_id=ana.id)
    repo.atualizar_bug(sessao, corrigido.id, status=Status.CORRIGIDO)

    assert len(repo.listar_bugs(sessao)) == 2
    assert len(repo.listar_bugs(sessao, status=Status.ABERTO)) == 1
    assert repo.listar_bugs(sessao, modulo="Checkout")[0].id == corrigido.id
    assert repo.listar_bugs(sessao, responsavel_id=ana.id)[0].id == corrigido.id
    assert repo.listar_bugs(sessao, severidade=Severidade.BAIXA) == []


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


def test_reatribuir_responsavel(sessao):
    ana = _novo_membro(sessao, "Ana")
    bruno = _novo_membro(sessao, "Bruno")
    bug = _novo_bug(sessao, responsavel_id=ana.id)

    atualizado = repo.atualizar_bug(sessao, bug.id, responsavel_id=bruno.id)

    assert atualizado is not None
    assert atualizado.responsavel is not None
    assert atualizado.responsavel.nome == "Bruno"


def test_reatribuir_para_responsavel_inexistente_levanta_erro(sessao):
    bug = _novo_bug(sessao)

    with pytest.raises(ValueError, match="não encontrado"):
        repo.atualizar_bug(sessao, bug.id, responsavel_id=999)


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
