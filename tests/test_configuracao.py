import tomllib
from pathlib import Path

CONFIGURACAO = Path(__file__).parents[1] / ".streamlit" / "config.toml"


def test_exportacao_de_dados_da_tabela_esta_desativada():
    configuracao = tomllib.loads(CONFIGURACAO.read_text(encoding="utf-8"))

    assert configuracao["client"]["disableDataExport"] is True
