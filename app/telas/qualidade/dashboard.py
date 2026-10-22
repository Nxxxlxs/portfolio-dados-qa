import streamlit as st

from app.telas.qualidade.fonte import obter_tabela
from core.qa.kpis import resumir_total

st.title("Qualidade")
tabela = obter_tabela()
total = resumir_total(tabela)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Bugs analisados", f"{total['bugs']:,}".replace(",", "."))
col2.metric("Mediana (dias)", f"{total['mediana_dias']:.1f}")
col3.metric("Média (dias)", f"{total['media_dias']:.1f}")
col4.metric("Taxa de reabertura", f"{total['taxa_reabertura']:.1%}")

st.page_link(
    "telas/qualidade/dados.py",
    label="Explorar dados",
    icon=":material/table_view:",
)
