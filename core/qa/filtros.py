from collections.abc import Collection
from datetime import date

import pandas as pd


def filtrar_categorias(
    tabela: pd.DataFrame, severidades: Collection[str], componentes: Collection[str]
) -> pd.DataFrame:
    """Mantém os bugs com a severidade e o componente escolhidos, em qualquer data."""
    passa = tabela["severidade"].isin(severidades) & tabela["componente"].isin(componentes)
    return tabela[passa]


def no_periodo(tabela: pd.DataFrame, coluna: str, inicio: date, fim: date) -> pd.DataFrame:
    """Mantém os bugs cuja data na coluna cai entre início e fim, incluindo o último dia."""
    fim_do_dia = pd.Timestamp(fim) + pd.Timedelta(days=1)
    passa = (tabela[coluna] >= pd.Timestamp(inicio)) & (tabela[coluna] < fim_do_dia)
    return tabela[passa]


def filtrar(
    tabela: pd.DataFrame,
    severidades: Collection[str],
    componentes: Collection[str],
    inicio: date,
    fim: date,
) -> pd.DataFrame:
    """Mantém os bugs criados no período, com a severidade e o componente escolhidos."""
    por_categoria = filtrar_categorias(tabela, severidades, componentes)
    return no_periodo(por_categoria, "criado_em", inicio, fim)
