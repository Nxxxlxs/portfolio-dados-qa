import streamlit as st

from app.qa.bugs.dialogos import dialogo_cadastro
from app.qa.bugs.listagem import exibir_lista

st.set_page_config(page_title="Bugs", layout="wide")

esquerda, direita = st.columns([5, 1])
esquerda.title("Bugs")
if direita.button("Novo bug", key="novo_bug", type="primary"):
    dialogo_cadastro()

exibir_lista()
