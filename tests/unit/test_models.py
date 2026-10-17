from core.models import Bug, Severidade, Status


def test_bug_novo_recebe_valores_padrao(sessao):
    bug = Bug(
        titulo="Botão salvar não responde",
        severidade=Severidade.ALTA,
        modulo="Cadastro",
    )
    sessao.add(bug)
    sessao.commit()

    salvo = sessao.get(Bug, bug.id)
    assert salvo.status == Status.ABERTO
    assert salvo.aberto_em is not None
    assert salvo.resolvido_em is None
    assert salvo.responsavel is None
