import streamlit as st
from sqlalchemy.orm import Session

import core.qa.models  # noqa: F401  (registra as tabelas em Base.metadata)
from core.database import Base, get_engine


@st.cache_resource
def obter_engine():
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine


def nova_sessao() -> Session:
    return Session(obter_engine())
