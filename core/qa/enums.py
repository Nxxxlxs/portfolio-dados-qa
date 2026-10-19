import enum


class Severidade(enum.Enum):
    BAIXA = "Baixa"
    MEDIA = "Média"
    ALTA = "Alta"
    CRITICA = "Crítica"


class Status(enum.Enum):
    ABERTO = "Aberto"
    EM_ANALISE = "Em análise"
    CORRIGIDO = "Corrigido"
    FECHADO = "Fechado"
    REABERTO = "Reaberto"


class Papel(enum.Enum):
    QA = "QA"
    DEV = "DEV"
