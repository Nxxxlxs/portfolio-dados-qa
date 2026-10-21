from streamlit.testing.v1 import AppTest

DADOS = "telas/qualidade/dados.py"


def _abrir(app_main: str) -> AppTest:
    return AppTest.from_file(app_main, default_timeout=10).run()


def test_menu_lateral_lista_o_modulo_de_qualidade(app_main):
    at = _abrir(app_main)

    assert at.sidebar.caption[0].value == "Módulos"


def test_pagina_de_dados_abre_pelo_roteador(app_main):
    at = _abrir(app_main).switch_page(DADOS).run()

    assert not at.exception
    assert at.title[0].value == "Dados de qualidade"
