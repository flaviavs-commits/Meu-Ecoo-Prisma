"""Uma linha do card de status."""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont

from ..tokens import FUNDO, SUPERFICIE, TEXTO_SUAVE, TEXTO_TENUE


class LinhaStatus:
    """Uma linha do card de status: icone, nome e badge colorida."""

    def __init__(self, pai: tk.Widget, rotulo: str, fontes: dict[str, tkfont.Font]) -> None:
        self.quadro = tk.Frame(pai, bg=SUPERFICIE)
        self.quadro.pack(fill="x", padx=22, pady=1)

        self.ponto = tk.Label(
            self.quadro, text="●", font=fontes["ponto"], bg=SUPERFICIE, fg=TEXTO_TENUE
        )
        self.ponto.pack(side="left", pady=8)

        tk.Label(
            self.quadro, text=rotulo, font=fontes["status_rotulo"],
            bg=SUPERFICIE, fg=TEXTO_SUAVE,
        ).pack(side="left", padx=(10, 0))

        # A badge e um Label com fundo proprio: e o unico jeito de ter
        # "pilula" sem Canvas, e aqui o retangulo suave basta.
        self.badge = tk.Label(
            self.quadro, text="—", font=fontes["badge"],
            bg=FUNDO, fg=TEXTO_TENUE, padx=11, pady=3,
        )
        self.badge.pack(side="right")

    def atualizar(self, texto: str, cor: str, fundo: str) -> None:
        self.ponto.config(fg=cor)
        self.badge.config(text=texto, fg=cor, bg=fundo)
