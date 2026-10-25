import math

import pandas as pd
import plotly.express as px
from plotly.graph_objects import Bar, Figure, Scatter

from core.qa.esquema import SEVERIDADES

COR_SEVERIDADE = {
    "blocker": "#d50000",
    "critical": "#f4511e",
    "major": "#ffa000",
    "normal": "#1f77b4",
    "minor": "#78909c",
    "trivial": "#b0bec5",
}

LIMITE_PARETO = 0.8
COR_PARETO_FORTE = "#00897b"
COR_PARETO_FRACA = "#80cbc4"
ALTURA_GRAFICO = 320
PASSOS_EM_MESES = (1, 2, 3, 6, 12)


def compactar(figura: Figure, altura: int = ALTURA_GRAFICO) -> Figure:
    """Retorna a figura com a altura fixa e as margens reduzidas,
    para os gráficos caberem melhor na tela."""
    figura.update_layout(height=altura, margin={"l": 10, "r": 10, "t": 30, "b": 10})
    return figura


def formatar_inteiro(valor: int) -> str:
    return f"{valor:,}".replace(",", ".")


def formatar_percentual(proporcao: float) -> str:
    return f"{proporcao:.1%}".replace(".", ",")


def eixo_de_meses(quantidade: int, maximo_de_marcas: int = 8) -> dict[str, str | int]:
    """Retorna as configurações para as marcas do eixo de meses:
    o menor intervalo que não passa do máximo de marcas."""
    passo = next((p for p in PASSOS_EM_MESES if math.ceil(quantidade / p) <= maximo_de_marcas), 12)
    if passo == 12:
        return {"dtick": "M12", "tickformat": "%Y", "tickangle": 0}
    return {"dtick": f"M{passo}", "tickformat": "%m<br>%Y", "tickangle": 0}


def grafico_criados_e_resolvidos(mensal: pd.DataFrame) -> Figure:
    """Retorna um gráfico de linhas com os bugs criados e resolvidos."""
    dados = mensal.assign(mes=mensal["mes"].dt.to_timestamp()).rename(
        columns={"criados": "Criados", "resolvidos": "Resolvidos"}
    )
    figura = px.line(
        dados,
        x="mes",
        y=["Criados", "Resolvidos"],
        labels={"mes": "Mês", "value": "Bugs", "variable": ""},
        color_discrete_sequence=["#1f77b4", "#ff7f0e"],
        markers=True,
    )
    figura.update_traces(hovertemplate="%{y}")

    figura.update_xaxes(eixo_de_meses(len(dados)), hoverformat="%m/%Y")
    figura.update_layout(hovermode="x unified")
    return compactar(figura)


def grafico_severidade(resumo: pd.DataFrame) -> Figure:
    """Retorna um gráfico de barras horizontais"""
    total = resumo["bugs"].sum()
    ordem = [s for s in SEVERIDADES if s in set(resumo["severidade"])]
    dados = resumo.set_index("severidade").loc[ordem].reset_index()
    dados["rotulo"] = [
        f"{formatar_inteiro(n)} ({formatar_percentual(n / total)})" for n in dados["bugs"]
    ]
    figura = px.bar(
        dados,
        x="bugs",
        y="severidade",
        orientation="h",
        text="rotulo",
        labels={"bugs": "Quantidade de Bugs", "severidade": "Severidade"},
    )
    figura.update_traces(
        marker_color=[COR_SEVERIDADE[s] for s in ordem],
        textposition="outside",
        cliponaxis=False,
        hovertemplate="%{x}",
    )
    figura.update_xaxes(range=[0, dados["bugs"].max() * 1.3], tickformat="d")
    figura.update_yaxes(categoryorder="array", categoryarray=ordem, autorange="reversed")
    figura.update_layout(width=260)
    return compactar(figura)


def grafico_tempo_resolucao(resumo: pd.DataFrame) -> Figure:
    """Retorna um gráfico com a mediana (barras) e a média (pontos) de dias até a resolução,
    por severidade."""
    ordem = [s for s in SEVERIDADES if s in set(resumo["severidade"])]
    dados = resumo.set_index("severidade").loc[ordem].reset_index()
    figura = Figure(
        data=[
            Bar(
                x=dados["severidade"],
                y=dados["mediana_dias"],
                orientation="v",
                name="Mediana",
                marker_color="#1f77b4",
                hovertemplate="%{y:.1f} dias",
            ),
            Scatter(
                x=dados["severidade"],
                y=dados["media_dias"],
                mode="markers",
                name="Média",
                marker={"symbol": "diamond", "size": 12, "color": "#ffffff"},
                hovertemplate="%{y:.1f} dias",
            ),
        ]
    )
    figura.update_yaxes(
        categoryorder="array", categoryarray=ordem, title_text="Dias", tickformat="d"
    )
    figura.update_xaxes(title_text="Severidade")
    figura.update_layout(hovermode="x unified")
    return compactar(figura)


def grafico_reabertura(resumo: pd.DataFrame) -> Figure:
    """Retorna um gráfico de barras horizontais da taxa de reabertura por severidade,
    com o tamanho do grupo."""
    ordem = [s for s in SEVERIDADES if s in set(resumo["severidade"])]
    dados = resumo.set_index("severidade").loc[ordem].reset_index()
    dados["rotulo"] = [
        f"{formatar_percentual(taxa)} (de {formatar_inteiro(n)})"
        for taxa, n in zip(dados["taxa_reabertura"], dados["bugs"], strict=True)
    ]
    figura = px.bar(
        dados,
        x="taxa_reabertura",
        y="severidade",
        orientation="h",
        text="rotulo",
        labels={"taxa_reabertura": "Taxa de reabertura", "severidade": "Severidade"},
    )
    figura.update_traces(
        textposition="outside",
        cliponaxis=False,
        hovertemplate="%{text}",
        marker_color=[COR_SEVERIDADE[s] for s in ordem],
    )
    figura.update_xaxes(tickformat=".0%", range=[0, dados["taxa_reabertura"].max() * 1.5])
    figura.update_yaxes(categoryorder="array", categoryarray=ordem, autorange="reversed")
    return compactar(figura)


def grafico_componentes(resumo: pd.DataFrame) -> Figure:
    """Retorna um gráfico de Pareto: barras de bugs por componente, do maior ao menor,
    e linha de acumulado em %."""
    dados = resumo.sort_values("bugs", ascending=False)
    total = dados["bugs"].sum()
    acumulado = dados["bugs"].cumsum() / total
    anterior = acumulado.shift(fill_value=0)
    cores = [COR_PARETO_FORTE if a < LIMITE_PARETO else COR_PARETO_FRACA for a in anterior]
    figura = Figure(
        data=[
            Bar(
                x=dados["componente"],
                y=dados["bugs"],
                name="Bugs",
                marker_color=cores,
                text=[
                    f"{formatar_inteiro(n)} ({formatar_percentual(n / total)})"
                    for n in dados["bugs"]
                ],
                textposition="outside",
                cliponaxis=False,
                hovertemplate="%{text}",
            ),
            Scatter(
                x=dados["componente"],
                y=acumulado,
                name="Acumulado",
                mode="lines+markers",
                yaxis="y2",
                line={"color": "#ffffff"},
                text=[formatar_percentual(a) for a in acumulado],
                hovertemplate="%{text}",
            ),
        ]
    )
    figura.update_layout(
        yaxis={"title": {"text": "Bugs"}, "tickformat": "d", "range": [0, total * 1.05]},
        yaxis2={
            "overlaying": "y",
            "side": "right",
            "range": [0, 1.05],
            "tickformat": ".0%",
            "dtick": 0.2,
            "showgrid": False,
        },
        legend={"orientation": "h", "x": 0, "y": 1.12},
        hovermode="x unified",
    )
    return compactar(figura)


def grafico_backlog(backlog: pd.DataFrame) -> Figure:
    """Retorna um gráfico de área dos bugs em aberto no fim de cada mês,
    a partir de backlog_por_mes."""
    dados = backlog.assign(mes=backlog["mes"].dt.to_timestamp())
    figura = px.area(
        dados,
        x="mes",
        y="backlog",
        labels={"mes": "Mês", "backlog": "Bugs em aberto"},
        color_discrete_sequence=["#5c6bc0"],
    )
    figura.update_traces(hovertemplate="%{y}")
    figura.update_xaxes(eixo_de_meses(len(dados)), hoverformat="%m/%Y")
    figura.update_yaxes(tickformat="d", rangemode="tozero")
    figura.update_layout(hovermode="x unified")
    return compactar(figura)
