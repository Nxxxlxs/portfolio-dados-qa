from core.qa.enums import Papel, Severidade
from core.qa.repositories import bugs, membros
from tests.ui.helpers import abrir, sessao_do_banco


def _gravar_bug(titulo="Erro no login", modulo="Login", responsavel=None, inativo=False) -> int:
    """Grava um bug direto no banco temporário e devolve o ID dele."""
    with sessao_do_banco() as sessao:
        responsavel_id = None
        if responsavel is not None:
            responsavel_id = membros.criar_membro(sessao, responsavel, Papel.DEV).id
        bug = bugs.criar_bug(
            sessao,
            titulo=titulo,
            severidade=Severidade.ALTA,
            modulo=modulo,
            responsavel_id=responsavel_id,
        )
        if inativo and responsavel_id is not None:
            membros.definir_ativo(sessao, responsavel_id, False)
        return bug.id


def _textos(at) -> list[str]:
    return [m.value for m in at.markdown]


def test_pagina_sem_bugs_mostra_aviso(banco_temporario, pagina_bugs):
    at = abrir(pagina_bugs)

    assert not at.exception
    assert at.title[0].value == "Bugs"
    assert "Nenhum bug" in at.info[0].value


def test_lista_mostra_os_bugs_gravados(banco_temporario, pagina_bugs):
    at = abrir(pagina_bugs)
    _gravar_bug("Erro no login", responsavel="Ana")
    _gravar_bug("Relatório vazio", modulo="Vendas")

    textos = _textos(at.run())

    assert {"Erro no login", "Relatório vazio", "Ana", "Vendas", "—"} <= set(textos)


def test_cada_bug_tem_botao_de_editar(banco_temporario, pagina_bugs):
    at = abrir(pagina_bugs)
    primeiro = _gravar_bug("Erro no login")
    segundo = _gravar_bug("Relatório vazio")

    chaves = [b.key for b in at.run().button]

    assert f"editar_{primeiro}" in chaves
    assert f"editar_{segundo}" in chaves


def test_novo_bug_abre_o_modal_de_cadastro(banco_temporario, pagina_bugs):
    at = abrir(pagina_bugs)

    at = at.button(key="novo_bug").click().run()

    assert at.text_input(key="titulo_bug").value == ""
    assert at.text_area(key="descricao_bug").value == ""


def test_editar_abre_o_modal_com_os_dados_do_bug(banco_temporario, pagina_bugs):
    at = abrir(pagina_bugs)
    bug_id = _gravar_bug("Erro no login", modulo="Login")

    at = at.run().button(key=f"editar_{bug_id}").click().run()

    assert at.text_input(key=f"titulo_editar_{bug_id}").value == "Erro no login"
    assert at.text_input(key=f"modulo_editar_{bug_id}").value == "Login"


def test_editar_mostra_responsavel_inativo_como_opcao(banco_temporario, pagina_bugs):
    at = abrir(pagina_bugs)
    bug_id = _gravar_bug(responsavel="Ana", inativo=True)

    at = at.run().button(key=f"editar_{bug_id}").click().run()

    opcoes = at.selectbox(key=f"responsavel_editar_{bug_id}").options
    assert opcoes == ["Sem responsável", "Ana (inativo)"]


def test_cada_bug_tem_botao_de_excluir(banco_temporario, pagina_bugs):
    at = abrir(pagina_bugs)
    primeiro = _gravar_bug("Erro no login")
    segundo = _gravar_bug("Relatório vazio")

    chaves = [b.key for b in at.run().button]

    assert f"excluir_{primeiro}" in chaves
    assert f"excluir_{segundo}" in chaves


def test_excluir_abre_confirmacao_com_o_bug_da_linha(banco_temporario, pagina_bugs):
    at = abrir(pagina_bugs)
    _gravar_bug("Erro no login")
    bug_id = _gravar_bug("Relatório vazio")

    at = at.run().button(key=f"excluir_{bug_id}").click().run()

    chaves = [b.key for b in at.button]
    assert f"confirmar_exclusao_{bug_id}" in chaves
    assert f"cancelar_exclusao_{bug_id}" in chaves
    assert any(f"#{bug_id} — Relatório vazio" in texto for texto in _textos(at))


def test_abrir_a_confirmacao_nao_exclui_o_bug(banco_temporario, pagina_bugs):
    at = abrir(pagina_bugs)
    bug_id = _gravar_bug("Erro no login")

    at.run().button(key=f"excluir_{bug_id}").click().run()

    with sessao_do_banco() as sessao:
        assert [b.id for b in bugs.listar_bugs(sessao)] == [bug_id]
