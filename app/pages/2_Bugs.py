import streamlit as st

from app.db import nova_sessao
from core.qa.enums import Severidade
from core.qa.repositories import bugs, membros

VALORES_INICIAIS = {
    "titulo_bug": "",
    "descricao_bug": "",
    "modulo_bug": "",
    "severidade_bug": list(Severidade)[0],
    "responsavel_bug": None,
}


def cadastrar_bug() -> None:
    estado = st.session_state
    try:
        with nova_sessao() as sessao:
            bugs.criar_bug(
                sessao,
                titulo=estado["titulo_bug"],
                severidade=estado["severidade_bug"],
                modulo=estado["modulo_bug"],
                descricao=estado["descricao_bug"],
                responsavel_id=estado["responsavel_bug"],
            )
    except ValueError as erro:
        estado["mensagem_bug"] = ("erro", str(erro))
        return

    estado["mensagem_bug"] = ("sucesso", f"Bug '{estado['titulo_bug'].strip()}' cadastrado.")
    for chave, valor in VALORES_INICIAIS.items():
        estado[chave] = valor


st.set_page_config(page_title="Bugs", layout="wide")
st.title("Bugs")

with nova_sessao() as sessao:
    ativos = {m.id: m.nome for m in membros.listar_membros(sessao)}

st.subheader("Novo bug")
with st.form("form_novo_bug", enter_to_submit=False):
    st.text_input("Título*", key="titulo_bug")
    st.text_area("Descrição", key="descricao_bug")
    st.selectbox(
        "Severidade",
        list(Severidade),
        format_func=lambda s: s.value,
        key="severidade_bug",
    )
    st.text_input("Módulo*", key="modulo_bug")
    st.selectbox(
        "Responsável",
        [None, *ativos],
        format_func=lambda i: "Sem responsável" if i is None else ativos[i],
        key="responsavel_bug",
    )
    st.form_submit_button("Cadastrar", key="cadastrar_bug", on_click=cadastrar_bug)

mensagem = st.session_state.pop("mensagem_bug", None)
if mensagem:
    tipo, texto = mensagem
    if tipo == "sucesso":
        st.success(texto)
    else:
        st.error(texto)

st.subheader("Lista de bugs")
with nova_sessao() as sessao:
    linhas = [
        {
            "ID": b.id,
            "Título": b.titulo,
            "Severidade": b.severidade.value,
            "Status": b.status.value,
            "Módulo": b.modulo,
            "Responsável": b.responsavel.nome if b.responsavel else "—",
            "Aberto em": b.aberto_em.isoformat(),
            "Resolvido em": b.resolvido_em.isoformat() if b.resolvido_em else "—",
        }
        for b in bugs.listar_bugs(sessao)
    ]

if linhas:
    st.dataframe(linhas, hide_index=True)
else:
    st.info("Nenhum bug cadastrado ainda.")
