from datetime import date

import pandas as pd

from core.qa.filtros import filtrar, no_periodo


def tabela_exemplo() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": [1, 2, 3],
            "criado_em": pd.to_datetime(
                ["2006-01-10 00:00", "2006-02-10 15:00", "2006-03-10 00:00"]
            ),
            "severidade": ["normal", "major", "normal"],
            "componente": ["Core", "UI", "Core"],
        }
    )


def test_filtrar_por_severidade_e_componente():
    resultado = filtrar(
        tabela_exemplo(), ["normal"], ["Core", "UI"], date(2006, 1, 1), date(2006, 12, 31)
    )

    assert resultado["id"].tolist() == [1, 3]


def test_filtrar_por_periodo_inclui_o_ultimo_dia_inteiro():
    resultado = filtrar(
        tabela_exemplo(),
        ["normal", "major"],
        ["Core", "UI"],
        date(2006, 2, 1),
        date(2006, 2, 10),
    )

    assert resultado["id"].tolist() == [2]


def test_no_periodo_usa_a_coluna_pedida_e_inclui_o_ultimo_dia():
    tabela = tabela_exemplo().assign(
        resolvido_em=pd.to_datetime(["2006-05-01 00:00", "2006-05-10 18:00", "2006-07-01 00:00"])
    )

    resultado = no_periodo(tabela, "resolvido_em", date(2006, 5, 1), date(2006, 5, 10))

    assert resultado["id"].tolist() == [1, 2]
