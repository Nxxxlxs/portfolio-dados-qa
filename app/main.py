import streamlit as st

st.set_page_config(page_title="Portfólio Dados & QA", layout="wide")

qualidade = st.Page(
    "telas/qualidade/dashboard.py",
    title="Qualidade",
    icon=":material/fact_check:",
    default=True,
)
qualidade_dados = st.Page(
    "telas/qualidade/dados.py",
    title="Dados de qualidade",
    url_path="qualidade-dados",
)

MODULOS = [qualidade]

pagina = st.navigation([*MODULOS, qualidade_dados], position="hidden")

with st.sidebar:
    st.caption("Módulos")
    for modulo in MODULOS:
        st.page_link(modulo)

pagina.run()
