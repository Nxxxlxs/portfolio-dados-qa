import pandas as pd

from core.qa.exibicao import COLUNAS_EXIBIDAS, preparar_para_exibicao


def test_preparar_para_exibicao_ordena_e_renomeia_sem_mexer_nos_valores():
    tabela = pd.DataFrame({coluna: [1] for coluna in reversed(COLUNAS_EXIBIDAS)})
    tabela["criado_em"] = pd.Timestamp("2006-01-05")

    resultado = preparar_para_exibicao(tabela)

    assert list(resultado.columns) == list(COLUNAS_EXIBIDAS.values())
    assert resultado["Criado em"].tolist() == [pd.Timestamp("2006-01-05")]
    assert resultado["ID"].tolist() == [1]
