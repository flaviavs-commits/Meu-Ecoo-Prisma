"""Primitivas de desenho em Canvas: cor, retangulo arredondado e a marca.

O Tk 8.6 nao tem canto arredondado nem importa SVG. Tudo aqui existe
para suprir isso com linha e poligono.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont


def fonte_disponivel(raiz: tk.Misc, preferida: str, reserva: str) -> str:
    """Devolve `preferida` se instalada, senao `reserva`."""
    return preferida if preferida in set(tkfont.families(raiz)) else reserva


def misturar(cor_a: str, cor_b: str, fracao: float) -> str:
    """Interpola duas cores hex. Usado nas transicoes de hover."""
    a = tuple(int(cor_a[i : i + 2], 16) for i in (1, 3, 5))
    b = tuple(int(cor_b[i : i + 2], 16) for i in (1, 3, 5))
    c = tuple(round(x + (y - x) * fracao) for x, y in zip(a, b))
    return f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}"


def retangulo_redondo(
    canvas: tk.Canvas, x1: float, y1: float, x2: float, y2: float, raio: float, **kw
) -> int:
    """Desenha um retangulo de cantos arredondados.

    O Tk nao tem primitiva para isso. O contorno e um poligono cujos
    cantos repetem pontos; `smooth=True` transforma essa repeticao na
    curva. E a unica forma de ter canto redondo real em Canvas.
    """
    pontos = [
        x1 + raio, y1,
        x2 - raio, y1,
        x2, y1,
        x2, y1 + raio,
        x2, y2 - raio,
        x2, y2,
        x2 - raio, y2,
        x1 + raio, y2,
        x1, y2,
        x1, y2 - raio,
        x1, y1 + raio,
        x1, y1,
    ]
    return canvas.create_polygon(pontos, smooth=True, splinesteps=16, **kw)


# Pontos do triangulo do prisma-logo-minimal.svg, convertidos do viewBox
# original (1254x1254). Mantidos em um so lugar para as tres aplicacoes
# (HUD, favicon, landing) desenharem a mesma forma exata.
LOGO_TOPO = (16.0, 6.38)
LOGO_ESQ = (6.35, 21.56)
LOGO_DIR = (25.65, 21.56)
LOGO_BASE = (16.0, 25.37)
LOGO_MEIO = (16.0, 17.51)

# Recorte nos limites reais do desenho (x: 6.35-25.65, y: 6.38-25.37),
# com margem simetrica de 1.2 - o mesmo viewBox usado em Logo.tsx e no
# favicon. Um enquadramento maior que o desenho (ex.: 0-32 inteiro) deixa
# folga desigual acima/abaixo do traco; ao lado de texto em caixa alta
# (sem descendentes), essa folga fazia o triangulo parecer flutuar acima
# da linha do texto em vez de alinhado com ele.
_LOGO_ORIGEM = (5.15, 5.18)
_LOGO_DIMENSAO = (21.8, 21.39)


def desenhar_logo_prisma(canvas: tk.Canvas, cor: str, tamanho: float = 30) -> None:
    """Desenha a marca do Prisma num Canvas quadrado de `tamanho` px."""
    escala = tamanho / max(_LOGO_DIMENSAO)

    def p(ponto: tuple[float, float]) -> tuple[float, float]:
        return (
            (ponto[0] - _LOGO_ORIGEM[0]) * escala,
            (ponto[1] - _LOGO_ORIGEM[1]) * escala,
        )

    topo, esq, dire, base, meio = (
        p(LOGO_TOPO), p(LOGO_ESQ), p(LOGO_DIR), p(LOGO_BASE), p(LOGO_MEIO)
    )
    largura_traco = max(1, round(1.6 * escala))
    kw = {"fill": cor, "width": largura_traco, "capstyle": "round", "joinstyle": "round"}

    canvas.create_line(*topo, *esq, *base, *dire, *topo, **kw)
    canvas.create_line(*topo, *base, **kw)
    canvas.create_line(*esq, *meio, *dire, **kw)
