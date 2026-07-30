"""Barra de rolagem desenhada, no lugar da `tk.Scrollbar`."""

from __future__ import annotations

import tkinter as tk

from ..tokens import CONSOLE_BARRA, CONSOLE_BARRA_ATIVA, CONSOLE_FUNDO


class BarraRolagem:
    """Barra de rolagem desenhada, no lugar da `tk.Scrollbar`.

    A `tk.Scrollbar` do Windows nao aceita estilo: sai sempre com aquele
    bloco cinza de widget de sistema, com setas nas pontas. Aqui a barra
    e um Canvas fino com um polegar arredondado que some quando nao ha o
    que rolar - o comportamento que a pessoa espera de um app atual.

    Liga-se ao Text pelos dois lados: o widget avisa a barra
    (`yscrollcommand`) e a barra move o widget (arrastar / clicar).
    """

    LARGURA = 6

    def __init__(self, pai: tk.Widget, alvo: tk.Text) -> None:
        self.alvo = alvo
        self.inicio = 0.0
        self.fim = 1.0
        self._arrastando = False
        self._origem = 0.0

        self.canvas = tk.Canvas(
            pai, width=self.LARGURA, bg=CONSOLE_FUNDO,
            highlightthickness=0, bd=0,
        )
        self.polegar = self.canvas.create_rectangle(
            0, 0, 0, 0, fill=CONSOLE_BARRA, outline="",
        )

        alvo.config(yscrollcommand=self.atualizar)
        self.canvas.bind("<Configure>", lambda _e: self._desenhar())
        self.canvas.bind("<Button-1>", self._clicar)
        self.canvas.bind("<B1-Motion>", self._arrastar)
        self.canvas.bind("<ButtonRelease-1>", self._soltar)
        self.canvas.bind("<Enter>", lambda _e: self.canvas.itemconfig(
            self.polegar, fill=CONSOLE_BARRA_ATIVA))
        self.canvas.bind("<Leave>", lambda _e: self.canvas.itemconfig(
            self.polegar, fill=CONSOLE_BARRA))

        # Roda do mouse tanto sobre o texto quanto sobre a propria barra.
        for widget in (alvo, self.canvas):
            widget.bind("<MouseWheel>", self._roda)

    def atualizar(self, inicio: str, fim: str) -> None:
        """Chamado pelo Text quando a visao muda."""
        self.inicio, self.fim = float(inicio), float(fim)
        self._desenhar()

    def _desenhar(self) -> None:
        altura = self.canvas.winfo_height()
        if altura <= 1:
            return

        # Nada a rolar: a barra some em vez de mostrar um trilho vazio.
        if self.inicio <= 0.0 and self.fim >= 1.0:
            self.canvas.itemconfig(self.polegar, state="hidden")
            return

        self.canvas.itemconfig(self.polegar, state="normal")
        topo = self.inicio * altura
        base = self.fim * altura

        # Polegar minimo: com muita saida a proporcao vira um risco de
        # 2px, impossivel de pegar com o mouse. Ao crescer, ele e
        # deslocado para dentro do trilho em vez de cortado - cortar
        # devolveria justamente o tamanho que se quis evitar.
        minimo = min(24.0, altura)
        if base - topo < minimo:
            meio = (topo + base) / 2
            topo = meio - minimo / 2
            base = topo + minimo
            if topo < 0:
                topo, base = 0.0, minimo
            elif base > altura:
                base, topo = altura, altura - minimo

        self.canvas.coords(self.polegar, 0, topo, self.LARGURA, base)

    def _fracao(self, y: int) -> float:
        altura = max(1, self.canvas.winfo_height())
        return min(1.0, max(0.0, y / altura))

    def _clicar(self, evento) -> None:
        altura = max(1, self.canvas.winfo_height())
        topo, base = self.inicio * altura, self.fim * altura
        if topo <= evento.y <= base:
            # Comecou sobre o polegar: arrasta a partir daqui.
            self._arrastando = True
            self._origem = evento.y - topo
        else:
            # Clique no trilho: pula direto para aquele ponto.
            visivel = self.fim - self.inicio
            self.alvo.yview_moveto(self._fracao(evento.y) - visivel / 2)

    def _arrastar(self, evento) -> None:
        if not self._arrastando:
            return
        self.alvo.yview_moveto(self._fracao(evento.y - self._origem))

    def _soltar(self, _evento) -> None:
        self._arrastando = False

    def _roda(self, evento) -> str:
        self.alvo.yview_scroll(-1 * (evento.delta // 120), "units")
        return "break"
