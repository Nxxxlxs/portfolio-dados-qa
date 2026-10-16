from pathlib import Path

from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).resolve().parents[1]
APP_MAIN = str(RAIZ / "app" / "main.py")


def test_app_carrega_sem_erros():
    at = AppTest.from_file(APP_MAIN).run()
    assert not at.exception
    assert at.title[0].value == "Portfólio Dados & QA"
