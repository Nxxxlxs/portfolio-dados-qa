import pandas as pd
import pandera.pandas as pa

SEVERIDADES = ["blocker", "critical", "major", "normal", "minor", "trivial"]
SEVERIDADES_NA_RESOLUCAO = [*SEVERIDADES, "enhancement"]

ESQUEMA_BUGS = pa.DataFrameSchema(
    {
        "id": pa.Column(int, unique=True),
        "criado_em": pa.Column("datetime64[s]"),
        "primeira_resolucao_em": pa.Column("datetime64[s]"),
        "dias_ate_resolucao": pa.Column(float, pa.Check.ge(0)),
        "severidade": pa.Column(str, pa.Check.isin(SEVERIDADES)),
        "severidade_na_resolucao": pa.Column(str, pa.Check.isin(SEVERIDADES_NA_RESOLUCAO)),
        "componente": pa.Column(str),
        "n_reaberturas": pa.Column(int, pa.Check.ge(0)),
        "reaberto": pa.Column(bool),
    },
    checks=[
        pa.Check(
            lambda tabela: tabela["primeira_resolucao_em"] >= tabela["criado_em"],
            error="primeira_resolucao_em anterior a criado_em",
        ),
        pa.Check(
            lambda tabela: tabela["reaberto"] == (tabela["n_reaberturas"] > 0),
            error="reaberto incoerente com n_reaberturas",
        ),
    ],
)


def validar_tabela(tabela: pd.DataFrame) -> pd.DataFrame:
    return ESQUEMA_BUGS.validate(tabela)
