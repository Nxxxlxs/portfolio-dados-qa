import pandas as pd

COLUNAS_EXIBIDAS = {
    "id": "ID",
    "criado_em": "Criado em",
    "primeira_resolucao_em": "Primeira resolução em",
    "dias_ate_resolucao": "Dias até a resolução",
    "severidade": "Severidade",
    "severidade_na_resolucao": "Severidade na resolução",
    "componente": "Componente",
    "reaberto": "Reaberto",
    "n_reaberturas": "Reaberturas",
}


def preparar_para_exibicao(tabela: pd.DataFrame) -> pd.DataFrame:
    """Retorna a tabela com as colunas na ordem de exibição e com nomes em português."""
    return tabela[list(COLUNAS_EXIBIDAS)].rename(columns=COLUNAS_EXIBIDAS)
