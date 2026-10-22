import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

from core.qa.download import PASTA_JDT

STATUS_RESOLVIDO = {"RESOLVED", "VERIFIED", "CLOSED"}


def ler_criacao(pasta: Path = PASTA_JDT) -> pd.DataFrame:
    raiz = ET.parse(pasta / "reports.xml").getroot()
    linhas = [
        (int(relatorio.attrib["id"]), int(relatorio.findtext("opening_time", default="")))
        for relatorio in raiz.findall("report")
    ]
    tabela = pd.DataFrame(linhas, columns=["id", "criado_em"])
    tabela["criado_em"] = pd.to_datetime(tabela["criado_em"], unit="s")
    return tabela


def ler_primeira_resolucao(pasta: Path = PASTA_JDT) -> pd.DataFrame:
    raiz = ET.parse(pasta / "bug_status.xml").getroot()
    linhas = []
    for relatorio in raiz.findall("report"):
        for mudanca in relatorio.findall("update"):
            status = mudanca.findtext("what", default="").strip()
            if status in STATUS_RESOLVIDO:
                quando = int(mudanca.findtext("when", default=""))
                linhas.append((int(relatorio.attrib["id"]), quando))
                break
    tabela = pd.DataFrame(linhas, columns=["id", "primeira_resolucao_em"])
    tabela["primeira_resolucao_em"] = pd.to_datetime(tabela["primeira_resolucao_em"], unit="s")
    return tabela


def ler_historico(arquivo: str, pasta: Path = PASTA_JDT) -> pd.DataFrame:
    raiz = ET.parse(pasta / arquivo).getroot()
    linhas = [
        (
            int(relatorio.attrib["id"]),
            int(mudanca.findtext("when", default="")),
            mudanca.findtext("what", default="").strip(),
        )
        for relatorio in raiz.findall("report")
        for mudanca in relatorio.findall("update")
    ]
    tabela = pd.DataFrame(linhas, columns=["id", "quando", "valor"])
    tabela["quando"] = pd.to_datetime(tabela["quando"], unit="s")
    return tabela


def ler_valor_final(arquivo: str, coluna: str, pasta: Path = PASTA_JDT) -> pd.DataFrame:
    historico = ler_historico(arquivo, pasta).sort_values("quando", kind="stable")
    ultimo = historico.groupby("id").tail(1)
    return ultimo[["id", "valor"]].rename(columns={"valor": coluna})


def ler_valor_na_resolucao(
    arquivo: str, coluna: str, resolucoes: pd.DataFrame, pasta: Path = PASTA_JDT
) -> pd.DataFrame:
    historico = ler_historico(arquivo, pasta).merge(resolucoes, on="id")
    ate_resolucao = historico[historico["quando"] <= historico["primeira_resolucao_em"]]
    ultimo = ate_resolucao.sort_values("quando", kind="stable").groupby("id").tail(1)
    return ultimo[["id", "valor"]].rename(columns={"valor": coluna})


def contar_reaberturas(resolucoes: pd.DataFrame, pasta: Path = PASTA_JDT) -> pd.DataFrame:
    historico = ler_historico("bug_status.xml", pasta).merge(resolucoes, on="id")
    depois = historico["quando"] >= historico["primeira_resolucao_em"]
    reabertos = historico[(historico["valor"] == "REOPENED") & depois]
    return reabertos.groupby("id").size().rename("n_reaberturas").reset_index()


def montar_tabela(pasta: Path = PASTA_JDT) -> pd.DataFrame:
    tabela = ler_criacao(pasta).merge(ler_primeira_resolucao(pasta), on="id", how="left")

    tabela = tabela.merge(ler_valor_final("severity.xml", "severidade", pasta), on="id", how="left")
    tabela = tabela.merge(
        ler_valor_final("component.xml", "componente", pasta), on="id", how="left"
    )

    resolucoes = tabela[["id", "primeira_resolucao_em"]]
    na_resolucao = ler_valor_na_resolucao(
        "severity.xml", "severidade_na_resolucao", resolucoes, pasta
    )

    tabela = tabela.merge(na_resolucao, on="id", how="left")

    reaberturas = contar_reaberturas(resolucoes, pasta)
    tabela = tabela.merge(reaberturas, on="id", how="left")
    tabela["n_reaberturas"] = tabela["n_reaberturas"].fillna(0).astype(int)
    tabela["reaberto"] = tabela["n_reaberturas"] > 0

    diferenca = tabela["primeira_resolucao_em"] - tabela["criado_em"]
    tabela["dias_ate_resolucao"] = diferenca.dt.total_seconds() / 86400

    return tabela
