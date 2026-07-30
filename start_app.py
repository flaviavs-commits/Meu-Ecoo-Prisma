#!/usr/bin/env python3
"""Porta de entrada do Prisma.

Abre o HUD: uma janela com o estado do ambiente ao vivo e as acoes em
cards (rodar, instalar, sincronizar, validar), mais um console funcional.

Este arquivo e so o gatilho. O HUD vive em `scripts/hud/`, um modulo por
responsabilidade - ver `scripts/hud/__init__.py` para o mapa. A regra que
mantem assim esta em `docs/CONSTITUICAO-MODULARIDADE.md`.

DESVIO REGISTRADO
    O `doktor SystemDesign/core/GUIA-START-APP-SCRIPT.md` pede um menu
    interativo *no terminal* (questionary/rich). Este projeto usa uma
    janela grafica no lugar, por decisao do Andre (2026-07-29). O motivo
    e o publico: a landing e um produto visual, e quem roda isso esta
    numa maquina com display.

    Consequencia aceita: nao ha porta de entrada em ambiente sem display
    (SSH, container, CI). Nesses casos, use os comandos direto:

        cd frontend && npm install
        cd frontend && npm run dev
        cd frontend && npm run lint && npm run build

    Ver IA.md, secao de decisoes.

Uso:
    python start_app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Permite rodar de qualquer pasta: sem isso, `python /outro/caminho/
# start_app.py` nao encontraria o pacote `scripts`.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from scripts.hud import abrir  # noqa: E402 - depende do sys.path acima


def main() -> int:
    return abrir()


if __name__ == "__main__":
    raise SystemExit(main())
