import pandas as pd


def contar_por_mes(tabela: pd.DataFrame, coluna: str) -> pd.DataFrame:
    """Conta quantos bugs caem em cada mês da coluna de data pedida, sem pular meses."""
    meses = tabela[coluna].dt.to_period("M")
    contagem = meses.value_counts()
    todos_os_meses = pd.period_range(contagem.index.min(), contagem.index.max(), freq="M")
    contagem = contagem.reindex(todos_os_meses, fill_value=0).sort_index()
    return contagem.rename_axis("mes").reset_index(name="bugs")


def criados_e_resolvidos_por_mes(tabela: pd.DataFrame) -> pd.DataFrame:
    """Devolve, por mês, quantos bugs foram criados e quantos tiveram a primeira resolução."""
    criados = contar_por_mes(tabela, "criado_em").rename(columns={"bugs": "criados"})
    resolvidos = contar_por_mes(tabela, "primeira_resolucao_em").rename(
        columns={"bugs": "resolvidos"}
    )
    juntos = criados.merge(resolvidos, on="mes", how="outer").sort_values("mes")
    colunas = ["criados", "resolvidos"]
    juntos[colunas] = juntos[colunas].fillna(0).astype(int)
    return juntos.reset_index(drop=True)


def so_resolvidos(tabela: pd.DataFrame) -> pd.DataFrame:
    """Mantém só os bugs que tiveram primeira resolução, os únicos que podem ser reabertos."""
    return tabela[tabela["primeira_resolucao_em"].notna()]


def resumir_por(tabela: pd.DataFrame, coluna: str) -> pd.DataFrame:
    """Resume os bugs já resolvidos de cada valor da coluna: tempo de resolução e reabertura."""
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
    """Resume todos os bugs já resolvidos: quantidade, tempo de resolução e reabertura."""
    resolvidos = so_resolvidos(tabela)
    return {
        "bugs": len(resolvidos),
        "media_dias": resolvidos["dias_ate_resolucao"].mean(),
        "mediana_dias": resolvidos["dias_ate_resolucao"].median(),
        "taxa_reabertura": resolvidos["reaberto"].mean(),
    }
