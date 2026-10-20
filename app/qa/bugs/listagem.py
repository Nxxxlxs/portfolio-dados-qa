import streamlit as st

from app.db import nova_sessao
from app.qa.bugs.dialogos import dialogo_edicao, dialogo_exclusao
from core.qa.repositories import bugs

CABECALHO = ["ID", "Título", "Severidade", "Status", "Módulo", "Responsável", "Aberto em", "", ""]
LARGURAS = [1, 4, 2, 2, 2, 2, 2, 1, 1]


def exibir_lista() -> None:
    with nova_sessao() as sessao:
        linhas = [
            (
                b.id,
                b.titulo,
                b.severidade.value,
                b.status.value,
                b.modulo,
                b.responsavel.nome if b.responsavel else "—",
                b.aberto_em.isoformat(),
            )
            for b in bugs.listar_bugs(sessao)
        ]

    if not linhas:
        st.info("Nenhum bug cadastrado ainda.")
        return

    for coluna, texto in zip(st.columns(LARGURAS), CABECALHO, strict=True):
        coluna.markdown(f"**{texto}**" if texto else "")

    for linha in linhas:
        bug_id = linha[0]
        colunas = st.columns(LARGURAS)
        for coluna, valor in zip(colunas, linha, strict=False):
            coluna.write(str(valor))
        if colunas[-2].button("Editar", key=f"editar_{bug_id}"):
            dialogo_edicao(bug_id)
        if colunas[-1].button("Excluir", key=f"excluir_{bug_id}"):
            dialogo_exclusao(bug_id)
