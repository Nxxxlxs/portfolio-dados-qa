import enum
from datetime import date

from sqlalchemy import Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


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


class Bug(Base):
    __tablename__ = "bugs"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(200))
    descricao: Mapped[str] = mapped_column(Text, default="")
    severidade: Mapped[Severidade] = mapped_column(Enum(Severidade))
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.ABERTO)
    modulo: Mapped[str] = mapped_column(String(100))
    responsavel: Mapped[str | None] = mapped_column(String(100), default=None)
    aberto_em: Mapped[date] = mapped_column(default=date.today)
    resolvido_em: Mapped[date | None] = mapped_column(default=None)
