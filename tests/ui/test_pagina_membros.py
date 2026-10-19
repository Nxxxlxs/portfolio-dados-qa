from streamlit.testing.v1 import AppTest

from core.qa.enums import Papel
from core.qa.repositories import membros
from tests.ui.helpers import abrir, sessao_do_banco

INDICE_DEV = list(Papel).index(Papel.DEV)


def _cadastrar(at: AppTest, nome: str, indice_papel: int = 0) -> AppTest:
    at.text_input(key="nome_membro").set_value(nome)
    at.selectbox(key="papel_membro").select_index(indice_papel)
    return at.button(key="btn_cadastrar_membro").click().run()


def _nomes_no_banco() -> list[str]:
    with sessao_do_banco() as sessao:
        return [m.nome for m in membros.listar_membros(sessao)]


def test_pagina_sem_membros_mostra_aviso(banco_temporario, pagina_membros):
    at = abrir(pagina_membros)

    assert not at.exception
    assert at.title[0].value == "Membros"
    assert "Nenhum membro" in at.info[0].value


def test_cadastrar_membro_grava_no_banco_e_lista(banco_temporario, pagina_membros):
    at = _cadastrar(abrir(pagina_membros), "Ana", INDICE_DEV)

    assert not at.exception
    assert "Ana" in at.success[0].value
    assert at.dataframe[0].value["Nome"].tolist() == ["Ana"]
    assert _nomes_no_banco() == ["Ana"]


def test_nome_duplicado_mostra_erro(banco_temporario, pagina_membros):
    at = _cadastrar(abrir(pagina_membros), "Ana")
    at = _cadastrar(at, " ana ")

    assert "Já existe" in at.error[0].value
    assert _nomes_no_banco() == ["Ana"]


def test_nome_vazio_mostra_erro(banco_temporario, pagina_membros):
    at = _cadastrar(abrir(pagina_membros), "   ")

    assert "obrigatório" in at.error[0].value
    assert _nomes_no_banco() == []
