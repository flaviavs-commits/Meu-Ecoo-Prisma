"""HUD de entrada do Prisma.

Pacote da janela que o `start_app.py` abre. Cada modulo tem uma
responsabilidade:

    caminhos.py   onde o projeto esta
    tokens.py     paleta, tipografia e medidas
    desenho.py    primitivas de Canvas (cor, canto redondo, marca)
    processos.py  abrir, ler e encerrar subprocesso
    ambiente.py   npm, dependencias, telas e porta
    fontes.py     resolve a tipografia disponivel
    widgets/      cada widget desenhado em seu arquivo
    layout.py     monta a janela
    status.py     mede o ambiente e pinta o card
    console.py    terminal embutido
    acoes.py      o que cada card faz
    janela.py     junta tudo na classe Hud

Uso normal:

    from scripts.hud import abrir
    abrir()
"""

from __future__ import annotations

import tkinter as tk

from .caminhos import FRONTEND
from .janela import Hud

__all__ = ["Hud", "abrir"]


def abrir() -> int:
    """Abre a janela do HUD. Devolve o codigo de saida do processo."""
    if not FRONTEND.is_dir():
        print(f"Pasta frontend nao encontrada em {FRONTEND}")
        return 1

    try:
        raiz = tk.Tk()
    except tk.TclError as exc:
        # Sem display (SSH, container, CI). O HUD nao tem como abrir.
        print(f"Nao foi possivel abrir a janela: {exc}\n")
        print("Sem interface grafica disponivel. Use os comandos direto:\n")
        print("  cd frontend && npm install")
        print("  cd frontend && npm run dev")
        print("  cd frontend && npm run lint && npm run build\n")
        return 1

    hud = Hud(raiz)
    raiz.protocol("WM_DELETE_WINDOW", hud.ao_fechar)
    raiz.mainloop()
    return 0
