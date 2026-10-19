from contextlib import contextmanager

from sqlalchemy.orm import Session
from streamlit.testing.v1 import AppTest

from core.database import get_engine


def abrir(pagina: str) -> AppTest:
    return AppTest.from_file(pagina, default_timeout=10).run()


@contextmanager
def sessao_do_banco():
    """Sessão no banco temporário do teste (lido da variável PORTFOLIO_DB_URL)."""
    engine = get_engine()
    try:
        with Session(engine) as sessao:
            yield sessao
    finally:
        engine.dispose()
