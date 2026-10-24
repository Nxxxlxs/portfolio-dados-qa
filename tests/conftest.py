from pathlib import Path

import pandas as pd
import pytest

from app.telas.qualidade.fonte import obter_tabela

RAIZ = Path(__file__).resolve().parents[1]


@pytest.fixture
def app_main() -> str:
    return str(RAIZ / "app" / "main.py")


@pytest.fixture(autouse=True)
def tabela_falsa(monkeypatch):
    """Troca a carga dos dados reais por uma tabela pequena em todos os testes."""
    tabela = pd.DataFrame(
        {
            "id": [1, 2],
            "criado_em": pd.to_datetime(["2006-01-01", "2006-01-02"]),
            "primeira_resolucao_em": pd.to_datetime(["2006-01-02", "2006-01-05"]),
            "dias_ate_resolucao": [1.0, 3.0],
            "severidade": ["normal", "major"],
            "componente": ["Core", "UI"],
            "reaberto": [True, False],
            "severidade_na_resolucao": ["normal", "major"],
            "n_reaberturas": [1, 0],
        }
    )
    monkeypatch.setattr("app.telas.qualidade.fonte.carregar_tabela", lambda: tabela)
    obter_tabela.clear()
    return tabela
