from collections.abc import Collection
from datetime import date

import pandas as pd


def filtrar(
    tabela: pd.DataFrame,
    severidades: Collection[str],
    componentes: Collection[str],
    inicio: date,
    fim: date,
) -> pd.DataFrame:
    fim_do_dia = pd.Timestamp(fim) + pd.Timedelta(days=1)
    passa = (
        tabela["severidade"].isin(severidades)
        & tabela["componente"].isin(componentes)
        & (tabela["criado_em"] >= pd.Timestamp(inicio))
        & (tabela["criado_em"] < fim_do_dia)
    )
    return tabela[passa]
