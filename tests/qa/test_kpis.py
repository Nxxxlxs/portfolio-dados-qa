from datetime import date

import pandas as pd
from pytest import approx

from core.qa.kpis import (
    backlog_por_mes,
    contar_por_mes,
    criados_e_resolvidos_por_mes,
    resumir_por,
    resumir_total,
)


def test_contar_por_mes_inclui_meses_sem_bugs_com_zero():
    tabela = pd.DataFrame({"criado_em": pd.to_datetime(["2006-01-05", "2006-01-20", "2006-03-10"])})

    resultado = contar_por_mes(tabela, "criado_em")

    assert resultado["mes"].tolist() == [
        pd.Period("2006-01"),
        pd.Period("2006-02"),
        pd.Period("2006-03"),
    ]
    assert resultado["bugs"].tolist() == [2, 0, 1]


def test_criados_e_resolvidos_por_mes_junta_os_dois_e_completa_com_zero():
    tabela = pd.DataFrame(
        {
            "criado_em": pd.to_datetime(["2006-01-05", "2006-01-20"]),
            "primeira_resolucao_em": pd.to_datetime(["2006-02-10", "2006-03-01"]),
        }
    )

    resultado = criados_e_resolvidos_por_mes(tabela)

    assert resultado["mes"].tolist() == [
        pd.Period("2006-01"),
        pd.Period("2006-02"),
        pd.Period("2006-03"),
    ]
    assert resultado["criados"].tolist() == [2, 0, 0]
    assert resultado["resolvidos"].tolist() == [0, 1, 1]


def test_resumir_por_calcula_media_mediana_e_taxa_de_reabertura_por_grupo():
    tabela = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "severidade": ["normal", "normal", "normal", "major", "normal"],
            "primeira_resolucao_em": [pd.Timestamp("2006-01-02")] * 4 + [pd.NaT],
            "dias_ate_resolucao": [1.0, 2.0, 9.0, 10.0, None],
            "reaberto": [True, False, False, True, False],
        }
    )

    resultado = resumir_por(tabela, "severidade").set_index("severidade")

    assert resultado.loc["normal", "bugs"] == 3
    assert resultado.loc["normal", "media_dias"] == 4.0
    assert resultado.loc["normal", "mediana_dias"] == 2.0
    assert resultado.loc["normal", "taxa_reabertura"] == approx(1 / 3)
    assert resultado.loc["major", "taxa_reabertura"] == 1.0


def test_resumir_total_ignora_bug_sem_resolucao():
    tabela = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "primeira_resolucao_em": [pd.Timestamp("2006-01-02")] * 4 + [pd.NaT],
            "dias_ate_resolucao": [1.0, 2.0, 9.0, 10.0, None],
            "reaberto": [True, False, False, True, False],
        }
    )

    resultado = resumir_total(tabela)

    assert resultado["bugs"] == 4
    assert resultado["media_dias"] == 5.5
    assert resultado["mediana_dias"] == 5.5
    assert resultado["taxa_reabertura"] == 0.5


def test_criados_e_resolvidos_no_periodo_usa_so_os_meses_e_datas_do_periodo():
    tabela = pd.DataFrame(
        {
            "criado_em": pd.to_datetime(["2006-01-05", "2006-01-20", "2006-03-10"]),
            "primeira_resolucao_em": pd.to_datetime(["2006-02-10", "2006-03-01", "2006-06-15"]),
        }
    )

    resultado = criados_e_resolvidos_por_mes(tabela, date(2006, 1, 1), date(2006, 3, 31))

    assert resultado["mes"].tolist() == [
        pd.Period("2006-01"),
        pd.Period("2006-02"),
        pd.Period("2006-03"),
    ]
    assert resultado["criados"].tolist() == [2, 0, 1]
    assert resultado["resolvidos"].tolist() == [0, 1, 1]


def test_backlog_por_mes_acumula_desde_o_inicio_e_mostra_so_o_periodo():
    tabela = pd.DataFrame(
        {
            "criado_em": pd.to_datetime(["2006-01-05", "2006-01-20", "2006-03-10"]),
            "primeira_resolucao_em": pd.to_datetime(["2006-02-10", "2006-03-01", "2006-06-15"]),
        }
    )

    resultado = backlog_por_mes(tabela, date(2006, 2, 1), date(2006, 5, 31))

    assert resultado["mes"].tolist() == [
        pd.Period("2006-02"),
        pd.Period("2006-03"),
        pd.Period("2006-04"),
        pd.Period("2006-05"),
    ]
    assert resultado["backlog"].tolist() == [1, 1, 1, 1]
