from streamlit.testing.v1 import AppTest


def test_app_carrega_sem_erros(app_main):
    at = AppTest.from_file(app_main).run()
    assert not at.exception
    assert at.title[0].value == "Qualidade"


def test_dashboard_mostra_os_quatro_cartoes(app_main):
    at = AppTest.from_file(app_main).run()

    assert not at.exception
    assert [m.label for m in at.metric] == [
        "Bugs analisados",
        "Mediana (dias)",
        "Média (dias)",
        "Taxa de reabertura",
    ]
    assert at.metric[0].value == "2"
    assert at.metric[3].value == "50.0%"
