import streamlit as st

CSS_ESPACO_TOPO = """
<style>
section.stMain .block-container,
.stAppViewBlockContainer,
.block-container {
    padding-top: 3rem;
    padding-bottom: 1rem;
}
</style>
"""


def aplicar_estilo() -> None:
    st.markdown(CSS_ESPACO_TOPO, unsafe_allow_html=True)
