import enum


class Severidade(enum.Enum):
    BAIXA = "baixa"
    MEDIA = "média"
    ALTA = "alta"
    CRITICA = "crítica"


class Status(enum.Enum):
    ABERTO = "aberto"
    EM_ANALISE = "em análise"
    CORRIGIDO = "corrigido"
    FECHADO = "fechado"
    REABERTO = "reaberto"


class Papel(enum.Enum):
    QA = "QA"
    DEV = "DEV"
