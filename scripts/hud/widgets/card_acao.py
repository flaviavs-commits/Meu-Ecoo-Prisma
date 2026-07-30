"""Card clicavel de acao, desenhado em Canvas."""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont

from ..desenho import misturar, retangulo_redondo
from ..tokens import (
    BORDA,
    BORDA_HOVER,
    FUNDO,
    MARCA,
    MARCA_ESCURA,
    RAIO,
    SOMBRA,
    SUPERFICIE,
    SUPERFICIE_HOVER,
    TEXTO,
    TEXTO_SUAVE,
    TEXTO_TENUE,
)


class CardAcao:
    """Card clicavel desenhado em Canvas.

    Existe porque `tk.Button` nao faz canto arredondado, sombra nem
    transicao - e era isso que dava o aspecto de formulario antigo. Aqui
    cada card e um Canvas proprio que redesenha as cores em hover.
    """

    ALTURA = 66

    def __init__(
        self,
        pai: tk.Widget,
        icone: str,
        titulo: str,
        descricao: str,
        callback,
        fontes: dict[str, tkfont.Font],
        primario: bool = False,
    ) -> None:
        self.callback = callback
        self.primario = primario
        self.habilitado = True
        self.fontes = fontes
        self._animacao: str | None = None
        self._fracao = 0.0

        self.canvas = tk.Canvas(
            pai,
            height=self.ALTURA,
            bg=FUNDO,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )

        self.icone = icone
        self.titulo = titulo
        self.descricao = descricao

        self.canvas.bind("<Configure>", lambda _e: self._desenhar())
        self.canvas.bind("<Enter>", lambda _e: self._animar(1.0))
        self.canvas.bind("<Leave>", lambda _e: self._animar(0.0))
        self.canvas.bind("<Button-1>", self._pressionar)
        self.canvas.bind("<ButtonRelease-1>", self._soltar)

    # -- desenho -------------------------------------------------------

    def _cores(self) -> tuple[str, str, str, str, str]:
        """(fundo, borda, cor do titulo, cor da descricao, cor do icone)."""
        if not self.habilitado:
            return (FUNDO, BORDA, TEXTO_TENUE, TEXTO_TENUE, TEXTO_TENUE)

        if self.primario:
            fundo = misturar(TEXTO, MARCA_ESCURA, self._fracao)
            return (fundo, fundo, "#ffffff", "#e8ded9", "#ffffff")

        return (
            misturar(SUPERFICIE, SUPERFICIE_HOVER, self._fracao),
            misturar(BORDA, BORDA_HOVER, self._fracao),
            TEXTO,
            TEXTO_SUAVE,
            MARCA if self._fracao > 0.5 else TEXTO_SUAVE,
        )

    def _desenhar(self) -> None:
        largura = self.canvas.winfo_width()
        if largura <= 1:
            return

        self.canvas.delete("all")
        fundo, borda, cor_titulo, cor_desc, cor_icone = self._cores()

        # Deslocamento sutil no hover: o card "sobe" 1px.
        topo = 1 - round(self._fracao)
        base = self.ALTURA - 3 - round(self._fracao)

        # "Sombra": contorno claro logo abaixo. Sem blur no Tk, entao a
        # profundidade vem de uma faixa deslocada, nao de um halo.
        if self.habilitado and not self.primario:
            retangulo_redondo(
                self.canvas, 1, topo + 3, largura - 1, base + 3, RAIO,
                fill=SOMBRA, outline="",
            )

        retangulo_redondo(
            self.canvas, 1, topo, largura - 1, base, RAIO,
            fill=fundo, outline=borda, width=1,
        )

        self.canvas.create_text(
            26, topo + 22, text=self.icone, font=self.fontes["icone"],
            fill=cor_icone, anchor="w",
        )
        self.canvas.create_text(
            58, topo + 21, text=self.titulo, font=self.fontes["card_titulo"],
            fill=cor_titulo, anchor="w",
        )
        self.canvas.create_text(
            58, topo + 41, text=self.descricao, font=self.fontes["card_desc"],
            fill=cor_desc, anchor="w",
        )

    # -- interacao -----------------------------------------------------

    def _animar(self, alvo: float) -> None:
        """Transicao de ~200 ms entre repouso e hover."""
        if not self.habilitado:
            return
        if self._animacao is not None:
            self.canvas.after_cancel(self._animacao)
            self._animacao = None

        def passo() -> None:
            delta = 0.18 if alvo > self._fracao else -0.18
            self._fracao = min(1.0, max(0.0, self._fracao + delta))
            self._desenhar()
            if abs(self._fracao - alvo) > 0.01:
                self._animacao = self.canvas.after(16, passo)
            else:
                self._animacao = None

        passo()

    def _pressionar(self, _evento) -> None:
        """Feedback discreto de clique: o card afunda por um instante."""
        if not self.habilitado:
            return
        self.canvas.move("all", 0, 1)

    def _soltar(self, evento) -> None:
        if not self.habilitado:
            return
        self._desenhar()
        # So dispara se o cursor ainda estiver sobre o card.
        if 0 <= evento.x <= self.canvas.winfo_width() and 0 <= evento.y <= self.ALTURA:
            self.callback()

    def definir_estado(self, habilitado: bool) -> None:
        if self.habilitado == habilitado:
            return
        self.habilitado = habilitado
        self.canvas.config(cursor="hand2" if habilitado else "")
        self._fracao = 0.0
        self._desenhar()

    def definir_conteudo(self, icone: str, titulo: str, descricao: str) -> None:
        self.icone, self.titulo, self.descricao = icone, titulo, descricao
        self._desenhar()

    def definir_primario(self, primario: bool) -> None:
        if self.primario != primario:
            self.primario = primario
            self._desenhar()
