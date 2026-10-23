from datetime import date

from streamlit.testing.v1 import AppTest


def test_app_carrega_sem_erros(app_main):
    at = AppTest.from_file(app_main).run()
    assert not at.exception
    assert "Dashboard de Qualidade de Software" in at.markdown[0].value


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


def test_filtro_de_severidade_atualiza_os_cartoes(app_main):
    at = AppTest.from_file(app_main).run()
    assert at.metric[0].value == "2"

    at.checkbox(key="severidade_normal").uncheck().run()

    assert not at.exception
    assert at.metric[0].value == "1"


def test_periodo_sem_data_final_pede_a_data_final(app_main):
    at = AppTest.from_file(app_main).run()

    at.date_input[0].set_value((date(2006, 1, 1),)).run()

    assert not at.exception
    assert at.info[0].value == "Escolha também a data final do período."


def test_sem_nenhum_bug_nos_filtros_mostra_aviso(app_main):
    at = AppTest.from_file(app_main).run()

    at.checkbox(key="severidade_normal").uncheck().run()
    at.checkbox(key="severidade_major").uncheck().run()

    assert not at.exception
    assert at.warning[0].value == "Nenhum bug encontrado com esses filtros."


def test_dashboard_mostra_os_graficos(app_main):
    at = AppTest.from_file(app_main).run()

    assert not at.exception
    assert [s.value for s in at.subheader] == [
        "Bugs criados e resolvidos por mês",
        "Tempo até a primeira resolução",
        "Bugs por severidade",
        "Taxa de reabertura",
    ]
