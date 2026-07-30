"""Resolve as fontes do HUD uma vez, com reserva para o Windows."""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont

from .desenho import fonte_disponivel
from .tokens import FAMILIA, FAMILIA_ICONE, FAMILIA_MONO


def preparar_fontes(raiz: tk.Misc) -> dict[str, tkfont.Font]:
    """Resolve a familia uma vez e devolve os pesos usados.

    `Inter` e a fonte da landing; quando nao esta instalada (o caso
    comum no Windows), `Segoe UI` e a substituta mais proxima.
    """
    familia = fonte_disponivel(raiz, FAMILIA, "Segoe UI")
    mono = fonte_disponivel(raiz, FAMILIA_MONO, "Consolas")
    icone = fonte_disponivel(raiz, FAMILIA_ICONE, "Segoe UI Symbol")

    return {
        "marca": tkfont.Font(family=familia, size=25, weight="bold"),
        "subtitulo": tkfont.Font(family=familia, size=10),
        "secao": tkfont.Font(family=familia, size=9, weight="bold"),
        "status_rotulo": tkfont.Font(family=familia, size=10),
        "badge": tkfont.Font(family=familia, size=9, weight="bold"),
        "ponto": tkfont.Font(family=familia, size=11),
        "card_titulo": tkfont.Font(family=familia, size=11, weight="bold"),
        "card_desc": tkfont.Font(family=familia, size=9),
        "icone": tkfont.Font(family=icone, size=15),
        "console": tkfont.Font(family=mono, size=10),
        "console_prompt": tkfont.Font(family=mono, size=11, weight="bold"),
        "dica": tkfont.Font(family=familia, size=8),
        "modal_titulo": tkfont.Font(family=familia, size=13, weight="bold"),
        "modal_botao": tkfont.Font(family=familia, size=9, weight="bold"),
        "modal_entrada": tkfont.Font(family=mono, size=11),
        "toast": tkfont.Font(family=familia, size=10, weight="bold"),
    }
