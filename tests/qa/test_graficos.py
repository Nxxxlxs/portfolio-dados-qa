import pandas as pd

from app.telas.qualidade.graficos import (
    COR_SEVERIDADE,
    grafico_criados_e_resolvidos,
    grafico_severidade,
)


def test_grafico_criados_e_resolvidos_tem_duas_linhas_com_os_valores_certos():
    mensal = pd.DataFrame(
        {
            "mes": pd.period_range("2006-01", "2006-03", freq="M"),
            "criados": [2, 0, 1],
            "resolvidos": [0, 1, 1],
        }
    )

    figura = grafico_criados_e_resolvidos(mensal)

    assert [linha.name for linha in figura.data] == ["Criados", "Resolvidos"]  # pyright: ignore[reportAttributeAccessIssue]
    assert list(figura.data[0].y) == [2, 0, 1]  # pyright: ignore[reportAttributeAccessIssue]
    assert list(figura.data[1].y) == [0, 1, 1]  # pyright: ignore[reportAttributeAccessIssue]


def test_eixo_mostra_todos_os_meses_em_periodo_curto_e_espaca_em_periodo_longo():
    def mensal(quantidade: int) -> pd.DataFrame:
        meses = pd.period_range("2006-01", periods=quantidade, freq="M")
        return pd.DataFrame({"mes": meses, "criados": 1, "resolvidos": 1})

    curto = grafico_criados_e_resolvidos(mensal(5))
    longo = grafico_criados_e_resolvidos(mensal(65))

    assert curto.layout.xaxis.dtick == "M1"
    assert longo.layout.xaxis.dtick == "M6"


def test_grafico_severidade_ordena_da_mais_grave_e_escreve_numero_e_porcentagem():
    resumo = pd.DataFrame({"severidade": ["normal", "critical"], "bugs": [3, 1]})

    figura = grafico_severidade(resumo)

    barras = figura.data[0]
    assert list(barras.y) == ["critical", "normal"]  # pyright: ignore[reportAttributeAccessIssue]
    assert list(barras.x) == [1, 3]  # pyright: ignore[reportAttributeAccessIssue]
    assert list(barras.text) == ["1 (25,0%)", "3 (75,0%)"]  # pyright: ignore[reportAttributeAccessIssue]
    assert list(barras.marker.color) == [COR_SEVERIDADE["critical"], COR_SEVERIDADE["normal"]]  # pyright: ignore[reportAttributeAccessIssue]
    assert figura.layout.xaxis.range[1] > 3  # pyright: ignore[reportAttributeAccessIssue]
