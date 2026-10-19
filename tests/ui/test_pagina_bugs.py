import pytest

from core.qa.enums import Papel, Severidade
from core.qa.repositories import bugs, membros
from tests.ui.helpers import abrir, sessao_do_banco

INDICE_ALTA = list(Severidade).index(Severidade.ALTA)
DESCRICAO_LONGA = "Passos para reproduzir: abrir o login e clicar em entrar sem preencher nada."


def _preencher(at, titulo="", descricao="", modulo="", severidade=0, responsavel=0):
    at.text_input(key="titulo_bug").set_value(titulo)
    at.text_area(key="descricao_bug").set_value(descricao)
    at.text_input(key="modulo_bug").set_value(modulo)
    at.selectbox(key="severidade_bug").select_index(severidade)
    at.selectbox(key="responsavel_bug").select_index(responsavel)
    return at


def _cadastrar(at):
    return at.button(key="cadastrar_bug").click().run()


def _bugs_no_banco():
    with sessao_do_banco() as sessao:
        return [
            (b.titulo, b.modulo, b.severidade, b.responsavel.nome if b.responsavel else None)
            for b in bugs.listar_bugs(sessao)
        ]


def _abrir_com_membros(pagina, *nomes_ativos, inativos=()):
    """Abre a página (que cria as tabelas), cadastra membros e recarrega."""
    at = abrir(pagina)
    with sessao_do_banco() as sessao:
        for nome in nomes_ativos:
            membros.criar_membro(sessao, nome, Papel.DEV)
        for nome in inativos:
            membro = membros.criar_membro(sessao, nome, Papel.DEV)
            membros.definir_ativo(sessao, membro.id, False)
    return at.run()


def test_pagina_sem_bugs_mostra_aviso(banco_temporario, pagina_bugs):
    at = abrir(pagina_bugs)

    assert not at.exception
    assert at.title[0].value == "Bugs"
    assert "Nenhum bug" in at.info[0].value


def test_cadastrar_bug_grava_no_banco_e_lista(banco_temporario, pagina_bugs):
    at = _abrir_com_membros(pagina_bugs, "Ana")

    _preencher(
        at,
        titulo="Erro no login",
        descricao=DESCRICAO_LONGA,
        modulo="Login",
        severidade=INDICE_ALTA,
        responsavel=1,
    )
    at = _cadastrar(at)

    assert not at.exception
    assert "Erro no login" in at.success[0].value
    tabela = at.dataframe[0].value
    assert tabela["Título"].tolist() == ["Erro no login"]
    assert tabela["Status"].tolist() == ["Aberto"]
    assert tabela["Responsável"].tolist() == ["Ana"]
    assert _bugs_no_banco() == [("Erro no login", "Login", Severidade.ALTA, "Ana")]


def test_cadastrar_bug_sem_responsavel(banco_temporario, pagina_bugs):
    at = _abrir_com_membros(pagina_bugs, "Ana")

    _preencher(at, titulo="Erro no login", modulo="Login", responsavel=0)
    at = _cadastrar(at)

    assert at.dataframe[0].value["Responsável"].tolist() == ["—"]
    assert _bugs_no_banco()[0][3] is None

    print(_bugs_no_banco())


def test_sucesso_limpa_os_campos(banco_temporario, pagina_bugs):
    at = abrir(pagina_bugs)

    _preencher(at, titulo="Erro no login", descricao=DESCRICAO_LONGA, modulo="Login")
    at = _cadastrar(at)

    assert at.text_input(key="titulo_bug").value == ""
    assert at.text_area(key="descricao_bug").value == ""
    assert at.text_input(key="modulo_bug").value == ""


@pytest.mark.parametrize(
    ("titulo", "modulo", "trecho"),
    [
        ("", "Login", "título"),
        ("Erro no login", "", "módulo"),
    ],
)
def test_erro_de_validacao_preserva_os_campos(
    banco_temporario, pagina_bugs, titulo, modulo, trecho
):
    at = abrir(pagina_bugs)

    _preencher(at, titulo=titulo, descricao=DESCRICAO_LONGA, modulo=modulo)
    at = _cadastrar(at)

    assert trecho in at.error[0].value
    assert at.text_input(key="titulo_bug").value == titulo
    assert at.text_area(key="descricao_bug").value == DESCRICAO_LONGA
    assert at.text_input(key="modulo_bug").value == modulo
    assert _bugs_no_banco() == []


def test_mensagem_some_na_interacao_seguinte(banco_temporario, pagina_bugs):
    at = abrir(pagina_bugs)
    _preencher(at, titulo="Erro no login", modulo="Login")
    at = _cadastrar(at)
    assert len(at.success) == 1

    at = at.run()

    assert len(at.success) == 0


def test_responsavel_lista_so_membros_ativos(banco_temporario, pagina_bugs):
    at = _abrir_com_membros(pagina_bugs, "Ana", inativos=("Bruno",))

    opcoes = at.selectbox(key="responsavel_bug").options

    assert opcoes == ["Sem responsável", "Ana"]
