import pandas as pd

from app.telas.qualidade.graficos import (
    COR_SEVERIDADE,
    grafico_criados_e_resolvidos,
    grafico_reabertura,
    grafico_severidade,
    grafico_tempo_resolucao,
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


def test_grafico_tempo_resolucao_tem_mediana_em_barras_e_media_em_pontos():
    resumo = pd.DataFrame(
        {
            "severidade": ["normal", "critical"],
            "mediana_dias": [2.8, 1.4],
            "media_dias": [60.2, 13.4],
        }
    )

    figura = grafico_tempo_resolucao(resumo)

    mediana, media = figura.data
    assert [mediana.name, media.name] == ["Mediana", "Média"]  # pyright: ignore[reportAttributeAccessIssue]
    assert list(mediana.x) == ["critical", "normal"]  # pyright: ignore[reportAttributeAccessIssue]
    assert list(mediana.y) == [1.4, 2.8]  # pyright: ignore[reportAttributeAccessIssue]
    assert list(media.y) == [13.4, 60.2]  # pyright: ignore[reportAttributeAccessIssue]
    assert figura.layout.yaxis.title.text == "Dias"  # pyright: ignore[reportAttributeAccessIssue]


def test_grafico_reabertura_ordena_e_mostra_taxa_com_tamanho_do_grupo():
    resumo = pd.DataFrame(
        {
            "severidade": ["normal", "critical"],
            "bugs": [1000, 8],
            "taxa_reabertura": [0.09, 0.125],
        }
    )

    figura = grafico_reabertura(resumo)

    barras = figura.data[0]
    assert list(barras.y) == ["critical", "normal"]  # pyright: ignore[reportAttributeAccessIssue]
    assert list(barras.x) == [0.125, 0.09]  # pyright: ignore[reportAttributeAccessIssue]
    assert list(barras.text) == ["12,5% (de 8)", "9,0% (de 1.000)"]  # pyright: ignore[reportAttributeAccessIssue]
