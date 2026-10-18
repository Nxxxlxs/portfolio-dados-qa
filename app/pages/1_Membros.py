import streamlit as st

from app.db import nova_sessao
from core.qa.enums import Papel
from core.qa.repositories import membros

st.set_page_config(page_title="Membros", layout="wide")
st.title("Membros")

st.subheader("Novo membro")
with st.form("form_novo_membro", clear_on_submit=True):
    nome = st.text_input("Nome", key="nome_membro")
    papel = st.selectbox(
        "Papel", key="papel_membro", options=list(Papel), format_func=lambda p: p.value
    )
    enviado = st.form_submit_button("Cadastrar", key="btn_cadastrar_membro")

if enviado:
    with nova_sessao() as sessao:
        try:
            membros.criar_membro(sessao, nome, papel)
            st.success(f"Membro '{nome.strip()}' cadastrado.")
        except ValueError as erro:
            st.error(str(erro))

st.subheader("Equipe")
with nova_sessao() as sessao:
    lista = membros.listar_membros(sessao, somente_ativos=False)
    linhas = [{"Nome": m.nome, "Papel": m.papel.value, "Ativo": m.ativo} for m in lista]

if linhas:
    st.dataframe(linhas, hide_index=True)
else:
    st.info("Nenhum membro cadastrado ainda.")
