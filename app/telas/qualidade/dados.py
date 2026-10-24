import streamlit as st

from app.telas.qualidade.fonte import obter_tabela
from core.qa.exibicao import preparar_para_exibicao

st.page_link(
    "telas/qualidade/dashboard.py",
    label="Voltar ao dashboard de qualidade",
    icon=":material/arrow_back:",
)
st.title("Dados de qualidade")

tabela = preparar_para_exibicao(obter_tabela())
st.caption(f"{len(tabela):,} bugs do JDT, com histórico de 2006 a 2011.".replace(",", "."))
st.dataframe(
    tabela,
    hide_index=True,
    width="stretch",
    column_config={
        "ID": st.column_config.NumberColumn(format="%d"),
        "Criado em": st.column_config.DatetimeColumn(format="DD/MM/YYYY HH:mm"),
        "Primeira resolução em": st.column_config.DatetimeColumn(format="DD/MM/YYYY HH:mm"),
        "Dias até a resolução": st.column_config.NumberColumn(format="%.1f"),
    },
)
