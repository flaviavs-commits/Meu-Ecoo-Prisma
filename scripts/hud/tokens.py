"""Tokens de design do HUD: paleta, tipografia e medidas.

A paleta vem de frontend/src/index.css (@theme) - o HUD e a landing sao o
mesmo produto. O console foge disso de proposito: terminal escuro e a
convencao que a pessoa ja reconhece.
"""

from __future__ import annotations

FUNDO = "#f7f5ee"          # creme da landing
SUPERFICIE = "#fffdf8"     # cards
SUPERFICIE_HOVER = "#fbf9f2"
SUPERFICIE_ALT = "#f0ece1"  # hover do botao secundario, um degrau mais forte
BORDA = "#e8e2d4"          # divisoria suave, nunca linha forte
BORDA_HOVER = "#d5cfc0"
SOMBRA = "#efeade"         # "sombra": contorno claro deslocado

TEXTO = "#1a1a1a"          # grafite
TEXTO_SUAVE = "#6b6862"
TEXTO_TENUE = "#6f6b63"

MARCA = "#c85a3c"          # terracota
MARCA_ESCURA = "#a8482f"

SUCESSO = "#356e45"
SUCESSO_FUNDO = "#e6efe6"
ALERTA = "#8a6015"
ALERTA_FUNDO = "#f7efdc"
ERRO = "#b83c2e"
ERRO_FUNDO = "#f7e4e0"
INFO = "#3f5f8e"
INFO_FUNDO = "#e4ebf5"

CONSOLE_FUNDO = "#151515"
CONSOLE_ENTRADA = "#1e1e1e"   # linha de comando, um degrau acima do fundo
CONSOLE_TEXTO = "#a8d5a8"
CONSOLE_SUAVE = "#8a8a8a"
CONSOLE_ERRO = "#e0796b"
CONSOLE_OK = "#7fc98a"
CONSOLE_COMANDO = "#e8c17a"   # eco do que a pessoa digitou
CONSOLE_BARRA = "#3a3a3a"
CONSOLE_BARRA_ATIVA = "#5a5a5a"

# `Inter` e a fonte da landing, mas raramente esta instalada no Windows.
# `Segoe UI` e a substituta mais proxima em metrica e desenho.
FAMILIA = "Inter"
FAMILIA_MONO = "Cascadia Code"

# Icones: a fonte nativa do Windows 11 desenha simbolos geometricos que
# herdam a cor do texto. Emoji colorido nao herda cor - ficaria com o
# mesmo tom no card escuro e no claro, e destoaria da paleta.
FAMILIA_ICONE = "Segoe Fluent Icons"

# Pontos de codigo da Segoe Fluent Icons usados nos cards.
ICONES = {
    "rodar": "",       # play
    "parar": "",       # stop
    "backend": "",     # servidor
    "navegador": "",   # globo
    "pacote": "",      # caixa
    "sincronizar": "", # sync
    "build": "",       # blocos
    "validar": "",     # check
    "porta": "",       # engrenagem
    "limpar": "",      # lixeira
    "fechar_porta": "", # cadeado com x
}

RAIO = 14                  # bordas suaves, 12-16px como pedido
ESPACO = 20                # respiro entre secoes
ALTURA_CONSOLE = 260       # piso do console, para caber saida de verdade
