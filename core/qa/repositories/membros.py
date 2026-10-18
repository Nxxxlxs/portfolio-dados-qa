from sqlalchemy import select
from sqlalchemy.orm import Session

from core.qa.enums import Papel
from core.qa.models import Membro


def criar_membro(sessao: Session, nome: str, papel: Papel) -> Membro:
    nome = nome.strip()
    if not nome:
        raise ValueError("O nome é obrigatório")

    nomes_existentes = {m.nome.casefold() for m in sessao.scalars(select(Membro))}
    if nome.casefold() in nomes_existentes:
        raise ValueError(f"Já existe um membro chamado '{nome}'")

    membro = Membro(nome=nome, papel=papel)
    sessao.add(membro)
    sessao.commit()
    return membro


def listar_membros(
    sessao: Session,
    papel: Papel | None = None,
    somente_ativos: bool = True,
) -> list[Membro]:
    consulta = select(Membro).order_by(Membro.nome)
    if papel is not None:
        consulta = consulta.where(Membro.papel == papel)
    if somente_ativos:
        consulta = consulta.where(Membro.ativo.is_(True))
    return list(sessao.scalars(consulta))


def definir_ativo(sessao: Session, membro_id: int, ativo: bool) -> Membro | None:
    membro = sessao.get(Membro, membro_id)
    if membro is None:
        return None
    membro.ativo = ativo
    sessao.commit()
    return membro
