#!/usr/bin/env python3
"""Traz as telas da aplicação do repositório de concepção para a landing.

CONTEXTO
    A landing (este repositório) é a vitrine pública. A aplicação em si
    - as telas de aluno, professor e diretor - vive em `Estudo-com-IA`,
    na pasta `app/`. Ao clicar em "Entrar", a landing abre essas
    telas definitivas.

    Enquanto o backend não existe, a forma mais simples de ligar as duas
    coisas é copiar as telas para `frontend/public/app/`, que o Vite
    serve como arquivo estático.

POR QUE UM SCRIPT, E NÃO CÓPIA MANUAL
    O `Estudo-com-IA` continua sendo a fonte da verdade: as telas são
    editadas lá. Este script traz a versão atual para cá de forma
    repetível, e o guia mínimo de qualidade pede automação em vez de
    edição manual quando a mudança se repete.

    A pasta de destino é ignorada pelo git: são arquivos derivados,
    não código deste repositório. Rode o script de novo quando as
    telas mudarem.

USO
    python scripts/sincronizar-app.py [--origem CAMINHO]

    Sem argumento, procura `Estudo-com-IA` ao lado deste repositório.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "frontend" / "public" / "app"

# Telas definitivas da aplicacao, mantidas na fonte `app/`.
TELAS = (
    "index.html",
    "login.html",
    "aluno.html",
    "professor.html",
    "diretor.html",
)

# Até 2026-08-03 havia aqui uma reescrita de `href="landing.html"` para
# `/`: a aplicação tinha uma landing própria, não copiada, e o link caía em
# 404 quando servido estaticamente. Essa landing foi apagada e as telas
# já apontam para a raiz - a cópia agora é literal.


def origem_padrao() -> Path:
    """Onde procurar o `app/`.

    A landing e as telas viviam em repositórios separados; hoje moram
    no mesmo, então a origem padrão é a raiz daqui. O `--origem`
    continua valendo para apontar outro checkout.
    """
    return RAIZ


def validar(origem: Path) -> Path | None:
    """Confere que a origem existe e tem o que precisamos."""
    app = origem / "frontend" / "app"

    if not origem.is_dir():
        print(f"  Repositorio de origem nao encontrado: {origem}")
        print("  Use --origem para indicar o caminho.")
        return None

    if not app.is_dir():
        print(f"  Pasta 'frontend/app/' nao encontrada em {origem}")
        return None

    faltando = [t for t in TELAS if not (app / t).is_file()]
    if faltando:
        print(f"  Telas ausentes em {app}: {', '.join(faltando)}")
        return None

    return app


def sincronizar(app: Path) -> int:
    """Copia telas e assets. Devolve a quantidade de arquivos copiados."""
    DESTINO.mkdir(parents=True, exist_ok=True)

    copiados = 0
    for tela in TELAS:
        shutil.copy2(app / tela, DESTINO / tela)
        print(f"    {tela}")
        copiados += 1

    assets_origem = app / "assets"
    if assets_origem.is_dir():
        assets_destino = DESTINO / "assets"
        if assets_destino.exists():
            shutil.rmtree(assets_destino)
        shutil.copytree(assets_origem, assets_destino)
        quantos = sum(1 for _ in assets_destino.rglob("*") if _.is_file())
        print(f"    assets/ ({quantos} arquivo(s))")
        copiados += quantos

    return copiados


def main() -> int:
    analisador = argparse.ArgumentParser(
        description="Sincroniza as telas da aplicacao para a landing."
    )
    analisador.add_argument(
        "--origem",
        type=Path,
        default=origem_padrao(),
        help="Caminho do repositorio Estudo-com-IA.",
    )
    argumentos = analisador.parse_args()

    origem = argumentos.origem.resolve()
    print(f"\n  Origem:  {origem}")
    print(f"  Destino: {DESTINO}\n")

    app = validar(origem)
    if app is None:
        return 1

    try:
        total = sincronizar(app)
    except OSError as erro:
        print(f"\n  Falha ao copiar: {erro}\n")
        return 1

    print(f"\n  {total} arquivo(s) sincronizado(s).")
    print("  A landing abre essas telas em /app/ ao clicar em Entrar.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
