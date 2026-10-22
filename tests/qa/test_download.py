import tarfile
from pathlib import Path

from core.qa.download import baixar_pacote, extrair_jdt


def criar_pacote_falso(caminho: Path) -> Path:
    origem = caminho.parent / "origem"
    for produto in ("JDT", "PDE"):
        pasta = origem / "eclipse" / produto
        pasta.mkdir(parents=True)
        (pasta / "reports.xml").write_text(f"<reports>{produto}</reports>")
    with tarfile.open(caminho, "w:gz") as tar:
        tar.add(origem / "eclipse", arcname="eclipse")
    return caminho


def test_extrair_jdt_pega_so_arquivos_do_jdt(tmp_path):
    pacote = criar_pacote_falso(tmp_path / "eclipse.tar.gz")
    destino = tmp_path / "jdt"

    extrair_jdt(pacote, destino)

    arquivos = list(destino.iterdir())
    assert [a.name for a in arquivos] == ["reports.xml"]
    assert "JDT" in arquivos[0].read_text()


def test_baixar_pacote_nao_baixa_de_novo_se_ja_existe(tmp_path):
    existente = tmp_path / "eclipse.tar.gz"
    existente.write_bytes(b"qualquer coisa")

    resultado = baixar_pacote(existente, url="http://endereco-invalido.test")

    assert resultado == existente
    assert existente.read_bytes() == b"qualquer coisa"


def test_baixar_pacote_baixa_e_salva_quando_nao_existe(tmp_path, monkeypatch):
    def baixar_falso(url, destino_arquivo):
        Path(destino_arquivo).write_bytes(b"conteudo baixado")

    monkeypatch.setattr("core.qa.download.urllib.request.urlretrieve", baixar_falso)
    destino = tmp_path / "data" / "raw" / "eclipse.tar.gz"

    resultado = baixar_pacote(destino, url="http://qualquer.test")

    assert resultado == destino
    assert destino.read_bytes() == b"conteudo baixado"
    assert not destino.with_suffix(".gz.part").exists()


def test_extrair_jdt_nao_extrai_de_novo_se_ja_existem_xml(tmp_path):
    destino = tmp_path / "jdt"
    destino.mkdir()
    (destino / "ja_existe.xml").write_text("<reports/>")
    pacote_inexistente = tmp_path / "nao_existe.tar.gz"

    resultado = extrair_jdt(pacote_inexistente, destino)

    assert resultado == destino
    assert [a.name for a in destino.iterdir()] == ["ja_existe.xml"]
