import streamlit as st

from app.telas.qualidade.fonte import obter_tabela
from app.telas.qualidade.graficos import grafico_criados_e_resolvidos, grafico_severidade
from core.qa.esquema import SEVERIDADES
from core.qa.filtros import filtrar, filtrar_categorias
from core.qa.kpis import criados_e_resolvidos_por_mes, resumir_por, resumir_total


def grupo_de_caixas(titulo: str, opcoes: list[str], chave: str, por_linha: int = 3) -> list[str]:
    st.caption(titulo)
    marcadas = []
    for inicio in range(0, len(opcoes), por_linha):
        linha = opcoes[inicio : inicio + por_linha]
        colunas = st.columns(por_linha)
        for coluna, opcao in zip(colunas, linha, strict=False):
            if coluna.checkbox(opcao, value=True, key=f"{chave}_{opcao}"):
                marcadas.append(opcao)
    return marcadas


col_title = st.markdown(
    "<h1 style='display: inline; font-size: 24px; margin-right: 10px;'>"
    "Dashboard de Qualidade de Software</h1>",
    unsafe_allow_html=True,
)

tabela = obter_tabela()

primeiro_dia = tabela["criado_em"].min().date()
ultimo_dia = tabela["criado_em"].max().date()

col_tilte, col_periodo, col_severidade, col_componente = st.columns([2, 1, 1, 1])

with col_periodo:
    periodo = st.date_input(
        "Período de criação",
        value=(primeiro_dia, ultimo_dia),
        min_value=primeiro_dia,
        max_value=ultimo_dia,
        format="DD/MM/YYYY",
    )

with col_severidade:
    severidades = grupo_de_caixas("Severidade", SEVERIDADES, "severidade")

with col_componente:
    componentes = grupo_de_caixas("Componente", sorted(tabela["componente"].unique()), "componente")

if len(periodo) != 2:
    st.info("Escolha também a data final do período.")
    st.stop()

filtrada = filtrar(tabela, severidades, componentes, periodo[0], periodo[1])
if filtrada.empty:
    st.warning("Nenhum bug encontrado com esses filtros.")
    st.stop()

total = resumir_total(filtrada)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Bugs analisados", f"{total['bugs']:,}".replace(",", "."))
col2.metric("Mediana (dias)", f"{total['mediana_dias']:.1f}")
col3.metric("Média (dias)", f"{total['media_dias']:.1f}")
col4.metric("Taxa de reabertura", f"{total['taxa_reabertura']:.1%}")

por_categoria = filtrar_categorias(tabela, severidades, componentes)
mensal = criados_e_resolvidos_por_mes(por_categoria, periodo[0], periodo[1])

col_mensal, col_severidade = st.columns([3, 2])

with col_mensal:
    st.subheader("Bugs criados e resolvidos por mês")
    por_categoria = filtrar_categorias(tabela, severidades, componentes)
    mensal = criados_e_resolvidos_por_mes(por_categoria, periodo[0], periodo[1])
    st.plotly_chart(grafico_criados_e_resolvidos(mensal), width="stretch")
    st.caption(
        "Criados e resolvidos são contados cada um pela sua própria data, dentro do período "
        f"escolhido. Os dados vão até {ultimo_dia:%d/%m/%Y}, então o último mês está incompleto. "
        "Os cartões acima consideram os bugs criados no período."
    )

with col_severidade:
    st.subheader("Bugs por severidade")
    st.plotly_chart(grafico_severidade(resumir_por(filtrada, "severidade")), width="stretch")
    st.caption("Bugs criados no período, com as categorias marcadas: a mesma base dos cartões.")

st.page_link(
    "telas/qualidade/dados.py",
    label="Explorar dados",
    icon=":material/table_view:",
)
