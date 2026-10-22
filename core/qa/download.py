import tarfile
import urllib.request
from pathlib import Path

URL_PACOTE = "https://github.com/ansymo/msr2013-bug_dataset/raw/master/data/eclipse.tar.gz"
PASTA_RAW = Path("data/raw")
ARQUIVO_PACOTE = PASTA_RAW / "eclipse.tar.gz"
PREFIXO_JDT = "eclipse/JDT/"
PASTA_JDT = PASTA_RAW / "jdt"


def baixar_pacote(destino: Path = ARQUIVO_PACOTE, url: str = URL_PACOTE) -> Path:
    if destino.exists():
        return destino
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporario = destino.with_suffix(destino.suffix + ".part")
    urllib.request.urlretrieve(url, temporario)
    temporario.replace(destino)
    return destino


def extrair_jdt(pacote: Path = ARQUIVO_PACOTE, destino: Path = PASTA_JDT) -> Path:
    if destino.exists() and any(destino.glob("*.xml")):
        return destino
    destino.mkdir(parents=True, exist_ok=True)
    with tarfile.open(pacote, "r:gz") as tar:
        for membro in tar.getmembers():
            if membro.isfile() and membro.name.startswith(PREFIXO_JDT):
                membro.name = Path(membro.name).name
                tar.extract(membro, destino, filter="data")
    return destino
