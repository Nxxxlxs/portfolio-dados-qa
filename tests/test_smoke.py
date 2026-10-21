from streamlit.testing.v1 import AppTest


def test_app_carrega_sem_erros(app_main):
    at = AppTest.from_file(app_main).run()
    assert not at.exception
    assert at.title[0].value == "Qualidade"
