from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]


@pytest.fixture
def app_main() -> str:
    return str(RAIZ / "app" / "main.py")
