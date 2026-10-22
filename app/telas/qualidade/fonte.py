import pandas as pd
import streamlit as st

from core.qa.carga import carregar_tabela


@st.cache_data(show_spinner="Carregando os dados do dashboard")
def obter_tabela() -> pd.DataFrame:
    """Devolve a tabela de bugs, calculada uma vez e guardada em memória pelo Streamlit."""
    return carregar_tabela()
