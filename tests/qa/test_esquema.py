import pandas as pd
import pytest
from pandera.errors import SchemaError

from core.qa.esquema import validar_tabela


def tabela_valida() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": [1, 2],
            "criado_em": pd.to_datetime(["2006-01-01", "2006-01-02"]).astype("datetime64[s]"),
            "primeira_resolucao_em": pd.to_datetime(["2006-01-02", "2006-01-04"]).astype(
                "datetime64[s]"
            ),
            "severidade": ["normal", "major"],
            "severidade_na_resolucao": ["normal", "enhancement"],
            "componente": ["Core", "UI"],
            "dias_ate_resolucao": [1.0, 2.0],
            "n_reaberturas": [0, 1],
            "reaberto": [False, True],
        }
    )


def test_tabela_valida_passa():
    tabela = tabela_valida()

    assert validar_tabela(tabela).equals(tabela)


def test_id_repetido_e_rejeitado():
    tabela = tabela_valida()
    tabela.loc[1, "id"] = 1

    with pytest.raises(SchemaError):
        validar_tabela(tabela)


def test_dias_negativos_sao_rejeitados():
    tabela = tabela_valida()
    tabela.loc[0, "dias_ate_resolucao"] = -1.0

    with pytest.raises(SchemaError):
        validar_tabela(tabela)


def test_resolucao_anterior_a_criacao_e_rejeitada():
    tabela = tabela_valida()
    tabela.loc[0, "primeira_resolucao_em"] = pd.Timestamp("2005-12-31").as_unit("s")

    with pytest.raises(SchemaError):
        validar_tabela(tabela)


def test_reaberto_incoerente_com_n_reaberturas_e_rejeitado():
    tabela = tabela_valida()
    tabela.loc[0, "reaberto"] = True

    with pytest.raises(SchemaError):
        validar_tabela(tabela)


def test_enhancement_so_vale_na_severidade_da_resolucao():
    tabela = tabela_valida()
    tabela.loc[0, "severidade"] = "enhancement"

    with pytest.raises(SchemaError):
        validar_tabela(tabela)
