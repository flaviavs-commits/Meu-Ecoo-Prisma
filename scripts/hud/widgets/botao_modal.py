"""Botao do modal, desenhado em Canvas."""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont

from ..desenho import misturar, retangulo_redondo
from ..tokens import (
    BORDA_HOVER,
    MARCA_ESCURA,
    SUPERFICIE,
    SUPERFICIE_ALT,
    TEXTO,
)


class BotaoModal:
    """Botao do modal, desenhado para combinar com os cards.

    O `tk.Button` nativo traz o relevo cinza do Windows e ignora cor de
    fundo em varios temas - o mesmo motivo que levou os cards para o
    Canvas.
    """

    ALTURA = 38

    def __init__(
        self,
        pai: tk.Widget,
        texto: str,
        callback,
        fonte: tkfont.Font,
        primario: bool = False,
        largura: int = 108,
    ) -> None:
        self.callback = callback
        self.texto = texto
        self.fonte = fonte
        self.primario = primario
        self._fracao = 0.0

        self.canvas = tk.Canvas(
            pai, width=largura, height=self.ALTURA, bg=SUPERFICIE,
            highlightthickness=0, bd=0, cursor="hand2",
        )
        self.canvas.bind("<Configure>", lambda _e: self._desenhar())
        self.canvas.bind("<Enter>", lambda _e: self._pintar(1.0))
        self.canvas.bind("<Leave>", lambda _e: self._pintar(0.0))
        self.canvas.bind("<ButtonRelease-1>", lambda _e: self.callback())

    def _pintar(self, fracao: float) -> None:
        self._fracao = fracao
        self._desenhar()

    def _desenhar(self) -> None:
        largura = self.canvas.winfo_width()
        if largura <= 1:
            return
        self.canvas.delete("all")

        if self.primario:
            fundo = misturar(TEXTO, MARCA_ESCURA, self._fracao)
            borda, cor = fundo, "#ffffff"
        else:
            fundo = misturar(SUPERFICIE, SUPERFICIE_ALT, self._fracao)
            borda, cor = BORDA_HOVER, TEXTO

        retangulo_redondo(
            self.canvas, 1, 1, largura - 1, self.ALTURA - 1, 9,
            fill=fundo, outline=borda, width=1,
        )
        self.canvas.create_text(
            largura / 2, self.ALTURA / 2, text=self.texto, font=self.fonte, fill=cor,
        )
