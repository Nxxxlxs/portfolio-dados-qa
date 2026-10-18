from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.qa.enums import Severidade, Status
from core.qa.models import Bug, Membro

CAMPOS_EDITAVEIS = {
    "titulo",
    "descricao",
    "severidade",
    "status",
    "modulo",
    "responsavel_id",
}


def criar_bug(
    sessao: Session,
    titulo: str,
    severidade: Severidade,
    modulo: str,
    descricao: str = "",
    responsavel_id: int | None = None,
) -> Bug:
    _validar_responsavel(sessao, responsavel_id)
    bug = Bug(
        titulo=titulo,
        severidade=severidade,
        modulo=modulo,
        descricao=descricao,
        responsavel_id=responsavel_id,
    )
    sessao.add(bug)
    sessao.commit()
    return bug


def obter_bug(sessao: Session, bug_id: int) -> Bug | None:
    return sessao.get(Bug, bug_id)


def listar_bugs(
    sessao: Session,
    status: Status | None = None,
    severidade: Severidade | None = None,
    modulo: str | None = None,
    responsavel_id: int | None = None,
) -> list[Bug]:
    consulta = select(Bug).order_by(Bug.id)
    if status is not None:
        consulta = consulta.where(Bug.status == status)
    if severidade is not None:
        consulta = consulta.where(Bug.severidade == severidade)
    if modulo is not None:
        consulta = consulta.where(Bug.modulo == modulo)
    if responsavel_id is not None:
        consulta = consulta.where(Bug.responsavel_id == responsavel_id)
    return list(sessao.scalars(consulta))


def atualizar_bug(sessao: Session, bug_id: int, **campos) -> Bug | None:
    bug = sessao.get(Bug, bug_id)
    if bug is None:
        return None

    invalidos = set(campos) - CAMPOS_EDITAVEIS
    if invalidos:
        raise ValueError(f"Campos não editáveis: {sorted(invalidos)}")

    if "responsavel_id" in campos:
        _validar_responsavel(sessao, campos["responsavel_id"])

    for nome, valor in campos.items():
        setattr(bug, nome, valor)
    if "status" in campos:
        _ajustar_resolucao(bug)

    sessao.commit()
    return bug


def excluir_bug(sessao: Session, bug_id: int) -> bool:
    bug = sessao.get(Bug, bug_id)
    if bug is None:
        return False
    sessao.delete(bug)
    sessao.commit()
    return True


def _validar_responsavel(sessao: Session, responsavel_id: int | None) -> None:
    if responsavel_id is None:
        return
    membro = sessao.get(Membro, responsavel_id)
    if membro is None:
        raise ValueError("Responsável não encontrado")
    if not membro.ativo:
        raise ValueError("Responsável inativo")


def _ajustar_resolucao(bug: Bug) -> None:
    if bug.status in (Status.CORRIGIDO, Status.FECHADO):
        if bug.resolvido_em is None:
            bug.resolvido_em = date.today()
    else:
        bug.resolvido_em = None
