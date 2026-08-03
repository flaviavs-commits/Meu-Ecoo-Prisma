import re
import unicodedata


def nome_seguro(nome: str) -> str:
    nome = nome.replace("\\", "/").split("/")[-1]
    nome = unicodedata.normalize("NFKC", nome)
    nome = "".join(caractere for caractere in nome if caractere.isprintable())
    nome = re.sub(r"[^A-Za-z0-9._-]", "_", nome)
    nome = nome.strip("._")[:120]
    return nome or "arquivo"
