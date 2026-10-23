import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure


def grafico_criados_e_resolvidos(mensal: pd.DataFrame) -> Figure:
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
