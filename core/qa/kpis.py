from datetime import date

import pandas as pd

from core.qa.filtros import no_periodo


def contar_por_mes(
    tabela: pd.DataFrame, coluna: str, meses: pd.PeriodIndex | None = None
) -> pd.DataFrame:
    """Retorna uma tabela com quantos bugs caem em cada mês da coluna de data pedida,
    sem pular meses."""
    do_mes = tabela[coluna].dt.to_period("M")
    contagem = do_mes.value_counts()
    if meses is None:
        meses = pd.period_range(contagem.index.min(), contagem.index.max(), freq="M")
    contagem = contagem.reindex(meses, fill_value=0).sort_index()
    return contagem.rename_axis("mes").reset_index(name="bugs")


def criados_e_resolvidos_por_mes(
    tabela: pd.DataFrame, inicio: date | None = None, fim: date | None = None
) -> pd.DataFrame:
    """Retorna a soma, por mês, dos bugs criados e os resolvidos, cada um pela própria data.

    Com início e fim, só entram os meses do período e as datas dentro dele.
    """
    meses = None
    base_criados, base_resolvidos = tabela, tabela
    if inicio is not None and fim is not None:
        meses = pd.period_range(inicio, fim, freq="M")
        base_criados = no_periodo(tabela, "criado_em", inicio, fim)
        base_resolvidos = no_periodo(tabela, "primeira_resolucao_em", inicio, fim)
    criados = contar_por_mes(base_criados, "criado_em", meses).rename(columns={"bugs": "criados"})
    resolvidos = contar_por_mes(base_resolvidos, "primeira_resolucao_em", meses).rename(
        columns={"bugs": "resolvidos"}
    )
    juntos = criados.merge(resolvidos, on="mes", how="outer").sort_values("mes")
    colunas = ["criados", "resolvidos"]
    juntos[colunas] = juntos[colunas].fillna(0).astype(int)
    return juntos.reset_index(drop=True)


def so_resolvidos(tabela: pd.DataFrame) -> pd.DataFrame:
    """Retorna uma tabela contendo só os bugs que tiveram primeira resolução,
    os únicos que podem ser reabertos."""
    return tabela[tabela["primeira_resolucao_em"].notna()]


def resumir_por(tabela: pd.DataFrame, coluna: str) -> pd.DataFrame:
    """Retorna os bugs já resolvidos de cada valor da coluna: tempo de resolução e reabertura."""
    resolvidos = so_resolvidos(tabela)
    return (
        resolvidos.groupby(coluna)
        .agg(
            bugs=("id", "count"),
            media_dias=("dias_ate_resolucao", "mean"),
            mediana_dias=("dias_ate_resolucao", "median"),
            taxa_reabertura=("reaberto", "mean"),
        )
        .reset_index()
    )


def resumir_total(tabela: pd.DataFrame) -> dict:
    """Retorna o resumo de todos os bugs já resolvidos com quantidade,
    tempo de resolução e reabertura."""
    resolvidos = so_resolvidos(tabela)
    return {
        "bugs": len(resolvidos),
        "media_dias": resolvidos["dias_ate_resolucao"].mean(),
        "mediana_dias": resolvidos["dias_ate_resolucao"].median(),
        "taxa_reabertura": resolvidos["reaberto"].mean(),
    }


def backlog_por_mes(tabela: pd.DataFrame, inicio: date, fim: date) -> pd.DataFrame:
    """Reorna os bugs em aberto no fim de cada mês do período,
    contando desde o primeiro bug da base."""
    mensal = criados_e_resolvidos_por_mes(tabela)
    mensal["backlog"] = (mensal["criados"] - mensal["resolvidos"]).cumsum()
    do_periodo = mensal["mes"].isin(pd.period_range(inicio, fim, freq="M"))
    return mensal.loc[do_periodo, ["mes", "backlog"]].reset_index(drop=True)
