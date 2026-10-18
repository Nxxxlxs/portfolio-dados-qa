import pytest

from core.qa.enums import Papel
from core.qa.repositories import membros


def test_criar_membro_nasce_ativo(novo_membro):
    membro = novo_membro("  Ana  ")

    assert membro.nome == "Ana"
    assert membro.ativo is True


def test_criar_membro_sem_nome_levanta_erro(novo_membro):
    with pytest.raises(ValueError, match="obrigatório"):
        novo_membro("   ")


def test_criar_membro_com_nome_repetido_levanta_erro(novo_membro):
    novo_membro("Ana")

    with pytest.raises(ValueError, match="Já existe"):
        novo_membro(" ana ")


def test_listar_membros_filtra_por_papel_e_ativos(sessao, novo_membro):
    ana = novo_membro("Ana", Papel.DEV)
    novo_membro("Bruno", Papel.QA)
    membros.definir_ativo(sessao, ana.id, False)

    assert [m.nome for m in membros.listar_membros(sessao)] == ["Bruno"]
    assert len(membros.listar_membros(sessao, somente_ativos=False)) == 2
    assert membros.listar_membros(sessao, papel=Papel.DEV) == []


def test_definir_ativo_de_membro_inexistente_retorna_none(sessao):
    assert membros.definir_ativo(sessao, 999, False) is None
