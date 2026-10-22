import pandas as pd

from core.qa.carga import (
    carregar_tabela,
    contar_reaberturas,
    ler_criacao,
    ler_primeira_resolucao,
    ler_valor_final,
    ler_valor_na_resolucao,
    montar_tabela,
)


def test_ler_criacao_devolve_id_e_data_de_cada_bug(tmp_path):
    (tmp_path / "reports.xml").write_text(
        "<reports>"
        '<report id="1"><opening_time>1136073600</opening_time></report>'
        '<report id="2"><opening_time>1136160000</opening_time></report>'
        "</reports>"
    )

    tabela = ler_criacao(tmp_path)

    assert list(tabela.columns) == ["id", "criado_em"]
    assert tabela["id"].tolist() == [1, 2]
    assert tabela["criado_em"].tolist() == [
        pd.Timestamp("2006-01-01"),
        pd.Timestamp("2006-01-02"),
    ]


def test_ler_primeira_resolucao_usa_resolved_verified_ou_closed(tmp_path):
    (tmp_path / "bug_status.xml").write_text(
        "<bug_status>"
        '<report id="1">'
        "<update><when>1136073600</when><what>NEW</what></update>"
        "<update><when>1136160000</when><what>RESOLVED</what></update>"
        "<update><when>1136246400</when><what>VERIFIED</what></update>"
        "</report>"
        '<report id="2">'
        "<update><when>1136073600</when><what>NEW</what></update>"
        "<update><when>1136246400</when><what>CLOSED</what></update>"
        "</report>"
        '<report id="3">'
        "<update><when>1136073600</when><what>NEW</what></update>"
        "<update><when>1136160000</when><what>ASSIGNED</what></update>"
        "</report>"
        "</bug_status>"
    )

    tabela = ler_primeira_resolucao(tmp_path)

    assert tabela["id"].tolist() == [1, 2]
    assert tabela["primeira_resolucao_em"].tolist() == [
        pd.Timestamp("2006-01-02"),
        pd.Timestamp("2006-01-03"),
    ]


def test_montar_tabela_calcula_dias_e_mantem_bug_sem_resolucao(tmp_path):
    (tmp_path / "reports.xml").write_text(
        "<reports>"
        '<report id="1"><opening_time>1136073600</opening_time></report>'
        '<report id="2"><opening_time>1136073600</opening_time></report>'
        "</reports>"
    )
    (tmp_path / "bug_status.xml").write_text(
        "<bug_status>"
        '<report id="1">'
        "<update><when>1136073600</when><what>NEW</what></update>"
        "<update><when>1136160000</when><what>RESOLVED</what></update>"
        "</report>"
        '<report id="2">'
        "<update><when>1136073600</when><what>NEW</what></update>"
        "</report>"
        "</bug_status>"
    )
    (tmp_path / "severity.xml").write_text(
        '<severity><report id="1"><update><when>1136073600</when><what>normal</what></update>'
        "</report>"
        '<report id="2"><update><when>1136073600</when><what>major</what></update>'
        "</report></severity>"
    )
    (tmp_path / "component.xml").write_text(
        '<component><report id="1"><update><when>1136073600</when><what>Core</what></update>'
        "</report>"
        '<report id="2"><update><when>1136073600</when><what>UI</what></update>'
        "</report></component>"
    )

    tabela = montar_tabela(tmp_path)

    assert tabela["id"].tolist() == [1, 2]
    assert tabela["dias_ate_resolucao"].iloc[0] == 1.0
    assert pd.isna(tabela["primeira_resolucao_em"].iloc[1])
    assert pd.isna(tabela["dias_ate_resolucao"].iloc[1])
    assert tabela["severidade"].tolist() == ["normal", "major"]
    assert tabela["componente"].tolist() == ["Core", "UI"]
    assert tabela["n_reaberturas"].tolist() == [0, 0]
    assert tabela["reaberto"].tolist() == [False, False]


def test_ler_valor_final_pega_a_ultima_mudanca_no_tempo(tmp_path):
    (tmp_path / "severity.xml").write_text(
        "<severity>"
        '<report id="1">'
        "<update><when>1136160000</when><what>major</what></update>"
        "<update><when>1136073600</when><what>normal</what></update>"
        "</report>"
        "</severity>"
    )

    tabela = ler_valor_final("severity.xml", "severidade", tmp_path)

    assert tabela["id"].tolist() == [1]
    assert tabela["severidade"].tolist() == ["major"]


def test_ler_valor_na_resolucao_ignora_mudancas_depois_da_resolucao(tmp_path):
    (tmp_path / "severity.xml").write_text(
        "<severity>"
        '<report id="1">'
        "<update><when>1136073600</when><what>normal</what></update>"
        "<update><when>1136160000</when><what>major</what></update>"
        "<update><when>1136332800</when><what>critical</what></update>"
        "</report>"
        "</severity>"
    )
    resolucoes = pd.DataFrame({"id": [1], "primeira_resolucao_em": [pd.Timestamp("2006-01-03")]})

    tabela = ler_valor_na_resolucao("severity.xml", "severidade_na_resolucao", resolucoes, tmp_path)

    assert tabela["severidade_na_resolucao"].tolist() == ["major"]


def test_contar_reaberturas_conta_so_as_que_vem_depois_da_primeira_resolucao(tmp_path):
    (tmp_path / "bug_status.xml").write_text(
        "<bug_status>"
        '<report id="1">'
        "<update><when>1136073600</when><what>NEW</what></update>"
        "<update><when>1136160000</when><what>RESOLVED</what></update>"
        "<update><when>1136246400</when><what>REOPENED</what></update>"
        "<update><when>1136332800</when><what>RESOLVED</what></update>"
        "<update><when>1136419200</when><what>REOPENED</what></update>"
        "</report>"
        '<report id="2">'
        "<update><when>1136073600</when><what>NEW</what></update>"
        "<update><when>1136160000</when><what>RESOLVED</what></update>"
        "</report>"
        "</bug_status>"
    )
    resolucoes = pd.DataFrame(
        {
            "id": [1, 2],
            "primeira_resolucao_em": [pd.Timestamp("2006-01-02"), pd.Timestamp("2006-01-02")],
        }
    )

    tabela = contar_reaberturas(resolucoes, tmp_path)

    assert tabela["id"].tolist() == [1]
    assert tabela["n_reaberturas"].tolist() == [2]


def test_carregar_tabela_baixa_extrai_monta_e_valida_nessa_ordem(monkeypatch):
    chamadas = []
    tabela_falsa = pd.DataFrame({"id": [1]})

    def baixar_falso():
        chamadas.append("baixar")

    def extrair_falso():
        chamadas.append("extrair")
        return "pasta-falsa"

    def montar_falso(pasta):
        chamadas.append(f"montar:{pasta}")
        return tabela_falsa

    def validar_falso(tabela):
        chamadas.append("validar")
        return tabela

    monkeypatch.setattr("core.qa.carga.baixar_pacote", baixar_falso)
    monkeypatch.setattr("core.qa.carga.extrair_jdt", extrair_falso)
    monkeypatch.setattr("core.qa.carga.montar_tabela", montar_falso)
    monkeypatch.setattr("core.qa.carga.validar_tabela", validar_falso)

    resultado = carregar_tabela()

    assert chamadas == ["baixar", "extrair", "montar:pasta-falsa", "validar"]
    assert resultado is tabela_falsa
