from datetime import date

import pytest

from core.qa.enums import Severidade, Status
from core.qa.models import Bug
from core.qa.repositories import bugs, membros


def test_criar_bug_sem_titulo_levanta_erro(sessao, novo_bug):
    with pytest.raises(ValueError, match="título"):
        novo_bug(titulo="   ")
    assert bugs.listar_bugs(sessao) == []


def test_criar_bug_sem_modulo_levanta_erro(sessao, novo_bug):
    with pytest.raises(ValueError, match="módulo"):
        novo_bug(modulo="")
    assert bugs.listar_bugs(sessao) == []


def test_criar_e_obter_bug(sessao, novo_bug):
    bug = novo_bug()

    encontrado = bugs.obter_bug(sessao, bug.id)
    assert encontrado is not None
    assert encontrado.titulo == "Erro no login"
    assert encontrado.status == Status.ABERTO


def test_criar_bug_com_responsavel(novo_membro, novo_bug):
    membro = novo_membro()

    bug = novo_bug(responsavel_id=membro.id)

    assert bug.responsavel.nome == "Ana"


def test_criar_bug_com_responsavel_inexistente_levanta_erro(novo_bug):
    with pytest.raises(ValueError, match="não encontrado"):
        novo_bug(responsavel_id=999)


def test_criar_bug_com_responsavel_inativo_levanta_erro(sessao, novo_membro, novo_bug):
    membro = novo_membro()
    membros.definir_ativo(sessao, membro.id, False)

    with pytest.raises(ValueError, match="inativo"):
        novo_bug(responsavel_id=membro.id)


def test_desativar_membro_mantem_o_historico_dos_bugs(sessao, novo_membro, novo_bug):
    membro = novo_membro()
    bug = novo_bug(responsavel_id=membro.id)

    membros.definir_ativo(sessao, membro.id, False)

    salvo = bugs.obter_bug(sessao, bug.id)
    assert salvo is not None
    assert salvo.responsavel_id == membro.id
    assert salvo.responsavel is not None
    assert salvo.responsavel.nome == "Ana"


def test_listar_filtra_por_status_modulo_e_responsavel(sessao, novo_membro, novo_bug):
    ana = novo_membro()
    novo_bug(modulo="Login")
    corrigido = novo_bug(modulo="Checkout", responsavel_id=ana.id)
    bugs.atualizar_bug(sessao, corrigido.id, status=Status.CORRIGIDO)

    assert len(bugs.listar_bugs(sessao)) == 2
    assert len(bugs.listar_bugs(sessao, status=Status.ABERTO)) == 1
    assert bugs.listar_bugs(sessao, modulo="Checkout")[0].id == corrigido.id
    assert bugs.listar_bugs(sessao, responsavel_id=ana.id)[0].id == corrigido.id
    assert bugs.listar_bugs(sessao, severidade=Severidade.BAIXA) == []


def test_listar_combina_filtros_com_and(sessao, novo_bug):
    novo_bug(modulo="Login", severidade=Severidade.ALTA)
    alvo = novo_bug(modulo="Login", severidade=Severidade.BAIXA)
    novo_bug(modulo="Checkout", severidade=Severidade.BAIXA)

    resultado = bugs.listar_bugs(sessao, modulo="Login", severidade=Severidade.BAIXA)

    assert [b.id for b in resultado] == [alvo.id]


def test_corrigir_bug_preenche_data_de_resolucao(sessao, novo_bug):
    bug = novo_bug()

    atualizado = bugs.atualizar_bug(sessao, bug.id, status=Status.CORRIGIDO)

    assert atualizado is not None
    assert atualizado.resolvido_em == date.today()


def test_reabrir_bug_limpa_data_de_resolucao(sessao, novo_bug):
    bug = novo_bug()
    bugs.atualizar_bug(sessao, bug.id, status=Status.FECHADO)

    reaberto = bugs.atualizar_bug(sessao, bug.id, status=Status.REABERTO)

    assert reaberto is not None
    assert reaberto.resolvido_em is None


def test_reatribuir_responsavel(sessao, novo_membro, novo_bug):
    ana = novo_membro("Ana")
    bruno = novo_membro("Bruno")
    bug = novo_bug(responsavel_id=ana.id)

    atualizado = bugs.atualizar_bug(sessao, bug.id, responsavel_id=bruno.id)

    assert atualizado is not None
    assert atualizado.responsavel is not None
    assert atualizado.responsavel.nome == "Bruno"


def test_reatribuir_para_responsavel_inexistente_levanta_erro(sessao, novo_bug):
    bug = novo_bug()

    with pytest.raises(ValueError, match="não encontrado"):
        bugs.atualizar_bug(sessao, bug.id, responsavel_id=999)


def test_atualizar_campo_invalido_levanta_erro(sessao, novo_bug):
    bug = novo_bug()

    with pytest.raises(ValueError, match="não editáveis"):
        bugs.atualizar_bug(sessao, bug.id, id=999)


def test_atualizar_bug_inexistente_retorna_none(sessao):
    assert bugs.atualizar_bug(sessao, 999, titulo="Novo título") is None


def test_excluir_bug(sessao, novo_bug):
    bug = novo_bug()

    assert bugs.excluir_bug(sessao, bug.id) is True
    assert bugs.obter_bug(sessao, bug.id) is None
    assert bugs.excluir_bug(sessao, bug.id) is False


@pytest.mark.parametrize(
    ("campo", "trecho"),
    [("titulo", "título"), ("modulo", "módulo")],
)
def test_atualizar_texto_obrigatorio_vazio_levanta_erro_e_nao_altera(
    sessao, novo_bug, campo, trecho
):
    bug = novo_bug()
    original = getattr(bug, campo)

    with pytest.raises(ValueError, match=trecho):
        bugs.atualizar_bug(sessao, bug.id, **{campo: "   "})

    assert getattr(bugs.obter_bug(sessao, bug.id), campo) == original


def test_atualizar_remove_espacos_do_titulo(sessao, novo_bug):
    bug = novo_bug()

    atualizado = bugs.atualizar_bug(sessao, bug.id, titulo="  Novo título  ")

    assert atualizado is not None
    assert atualizado.titulo == "Novo título"


def test_manter_responsavel_inativo_ao_editar_outros_campos(sessao, novo_membro, novo_bug):
    ana = novo_membro("Ana")
    bug = novo_bug(responsavel_id=ana.id)
    membros.definir_ativo(sessao, ana.id, False)

    atualizado = bugs.atualizar_bug(sessao, bug.id, titulo="Novo título", responsavel_id=ana.id)

    assert atualizado is not None
    assert atualizado.titulo == "Novo título"
    assert atualizado.responsavel_id == ana.id


def test_reatribuir_para_responsavel_inativo_levanta_erro(sessao, novo_membro, novo_bug):
    bruno = novo_membro("Bruno")
    membros.definir_ativo(sessao, bruno.id, False)
    bug: Bug = novo_bug()

    with pytest.raises(ValueError, match="inativo"):
        bugs.atualizar_bug(sessao, bug.id, responsavel_id=bruno.id)

    assert bug.responsavel_id is None


def test_remover_responsavel(sessao, novo_membro, novo_bug):
    ana = novo_membro("Ana")
    bug = novo_bug(responsavel_id=ana.id)

    atualizado = bugs.atualizar_bug(sessao, bug.id, responsavel_id=None)

    assert atualizado is not None
    assert atualizado.responsavel_id is None
