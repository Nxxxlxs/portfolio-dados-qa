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


def formatar_inteiro(valor: int) -> str:
    return f"{valor:,}".replace(",", ".")


def formatar_percentual(proporcao: float) -> str:
    return f"{proporcao:.1%}".replace(".", ",")


def grafico_criados_e_resolvidos(mensal: pd.DataFrame) -> Figure:
    """Linhas"""
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
    meses = len(dados)
    passo = "M1" if meses <= 12 else "M3" if meses <= 36 else "M6"
    figura.update_xaxes(dtick=passo, tickformat="%m/%Y", hoverformat="%m/%Y")
    figura.update_layout(hovermode="x unified")
    return figura


def grafico_severidade(resumo: pd.DataFrame) -> Figure:
    """Barras horizontais"""
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
    return figura


def grafico_tempo_resolucao(resumo: pd.DataFrame) -> Figure:
    """Mediana (barras) e média (pontos) de dias até a resolução, por severidade."""
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
    return figura


def grafico_reabertura(resumo: pd.DataFrame) -> Figure:
    """Barras horizontais da taxa de reabertura por severidade, com o tamanho do grupo."""
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
    return figura
