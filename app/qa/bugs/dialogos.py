import streamlit as st

from app.db import nova_sessao
from core.qa.enums import Severidade, Status
from core.qa.repositories import bugs, membros


@st.dialog("Cadastrar bug")
def dialogo_cadastro() -> None:
    with nova_sessao() as sessao:
        ativos = {m.id: m.nome for m in membros.listar_membros(sessao)}

    with st.form("form_novo_bug", enter_to_submit=False):
        titulo = st.text_input("Título", key="titulo_bug")
        descricao = st.text_area("Descrição", key="descricao_bug")
        severidade = st.selectbox(
            "Severidade",
            list(Severidade),
            format_func=lambda s: s.value,
            key="severidade_bug",
        )
        modulo = st.text_input("Módulo", key="modulo_bug")
        responsavel_id = st.selectbox(
            "Responsável",
            [None, *ativos],
            format_func=lambda i: "Sem responsável" if i is None else ativos[i],
            key="responsavel_bug",
        )
        enviado = st.form_submit_button("Cadastrar", key="cadastrar_bug")

    if enviado:
        try:
            with nova_sessao() as sessao:
                bugs.criar_bug(
                    sessao,
                    titulo=titulo,
                    severidade=severidade,
                    modulo=modulo,
                    descricao=descricao,
                    responsavel_id=responsavel_id,
                )
        except ValueError as erro:
            st.error(str(erro))
        else:
            st.toast(f"Bug '{titulo.strip()}' cadastrado.")
            st.rerun()


@st.dialog("Editar bug")
def dialogo_edicao(bug_id: int) -> None:
    with nova_sessao() as sessao:
        bug = bugs.obter_bug(sessao, bug_id)
        if bug is None:
            st.error("Este bug não existe mais.")
            return
        atual = {
            "titulo": bug.titulo,
            "descricao": bug.descricao,
            "severidade": bug.severidade,
            "status": bug.status,
            "modulo": bug.modulo,
            "responsavel_id": bug.responsavel_id,
        }
        nomes: dict[int | None, str] = {None: "Sem responsável"}
        nomes.update({m.id: m.nome for m in membros.listar_membros(sessao)})
        if bug.responsavel is not None and bug.responsavel_id not in nomes:
            nomes[bug.responsavel_id] = f"{bug.responsavel.nome} (inativo)"

    with st.form(f"form_editar_bug_{bug_id}", enter_to_submit=False):
        titulo = st.text_input("Título", value=atual["titulo"], key=f"titulo_editar_{bug_id}")
        descricao = st.text_area(
            "Descrição", value=atual["descricao"], key=f"descricao_editar_{bug_id}"
        )
        severidade = st.selectbox(
            "Severidade",
            list(Severidade),
            index=list(Severidade).index(atual["severidade"]),
            format_func=lambda s: s.value,
            key=f"severidade_editar_{bug_id}",
        )
        status = st.selectbox(
            "Status",
            list(Status),
            index=list(Status).index(atual["status"]),
            format_func=lambda s: s.value,
            key=f"status_editar_{bug_id}",
        )
        modulo = st.text_input("Módulo", value=atual["modulo"], key=f"modulo_editar_{bug_id}")
        responsavel_id = st.selectbox(
            "Responsável",
            list(nomes),
            index=list(nomes).index(atual["responsavel_id"]),
            format_func=lambda i: nomes[i],
            key=f"responsavel_editar_{bug_id}",
        )
        salvo = st.form_submit_button("Salvar alterações", key=f"salvar_bug_{bug_id}")

    if salvo:
        try:
            with nova_sessao() as sessao:
                bugs.atualizar_bug(
                    sessao,
                    bug_id,
                    titulo=titulo,
                    descricao=descricao,
                    severidade=severidade,
                    status=status,
                    modulo=modulo,
                    responsavel_id=responsavel_id,
                )
        except ValueError as erro:
            st.error(str(erro))
        else:
            st.toast(f"Bug #{bug_id} atualizado.")
            st.rerun()


@st.dialog("Excluir bug")
def dialogo_exclusao(bug_id: int) -> None:
    with nova_sessao() as sessao:
        bug = bugs.obter_bug(sessao, bug_id)
        titulo = bug.titulo if bug is not None else None

    if titulo is None:
        st.error("Este bug não existe mais.")
        return

    st.write(f"Excluir o bug **#{bug_id} — {titulo}**? Esta ação não pode ser desfeita.")
    confirmar, cancelar = st.columns(2)

    if confirmar.button("Excluir", type="primary", key=f"confirmar_exclusao_{bug_id}"):
        with nova_sessao() as sessao:
            bugs.excluir_bug(sessao, bug_id)
        st.toast(f"Bug #{bug_id} excluído.")
        st.rerun()

    if cancelar.button("Cancelar", key=f"cancelar_exclusao_{bug_id}"):
        st.rerun()
