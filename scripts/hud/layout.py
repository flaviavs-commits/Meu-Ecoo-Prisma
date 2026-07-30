"""Montagem visual da janela: cabecalho, status, grade de acoes e console.

Mixin da classe `Hud`. Cria os widgets e os guarda em `self`; nao contem
regra de negocio.
"""

from __future__ import annotations

import tkinter as tk

from .desenho import desenhar_logo_prisma
from .tokens import (
    ALTURA_CONSOLE,
    BORDA,
    CONSOLE_COMANDO,
    CONSOLE_ENTRADA,
    CONSOLE_ERRO,
    CONSOLE_FUNDO,
    CONSOLE_OK,
    CONSOLE_SUAVE,
    CONSOLE_TEXTO,
    ESPACO,
    FUNDO,
    ICONES,
    SUPERFICIE,
    TEXTO,
    TEXTO_TENUE,
)
from .widgets import BarraRolagem, CardAcao, LinhaStatus


class LayoutMixin:
    """Constroi a janela. Cada `_montar_*` cuida de uma secao."""

    def _montar(self) -> None:
        self.raiz.title("Prisma")
        self.raiz.configure(bg=FUNDO)
        # Mais largo para o console caber linha de comando sem quebrar.
        # A altura e definida depois de montar tudo (`_ajustar_altura`),
        # a partir do que o conteudo realmente pede - fixar um numero
        # aqui espremia o console, a unica secao elastica.
        self.raiz.geometry("980x1020")

        # Coluna central com margens generosas. Usa `grid` em vez de
        # `pack` para o console poder ser a unica secao que cresce: com
        # `pack`, o `expand` reparte a sobra e o console acabava menor do
        # que a altura pedida.
        self.coluna = tk.Frame(self.raiz, bg=FUNDO)
        self.coluna.pack(fill="both", expand=True, padx=ESPACO)
        self.coluna.columnconfigure(0, weight=1)
        self.coluna.rowconfigure(3, weight=1)  # so a linha do console cresce

        self._montar_cabecalho()
        self._montar_status()
        self._montar_acoes()
        self._montar_console()

    def _montar_cabecalho(self) -> None:
        cabecalho = tk.Frame(self.coluna, bg=FUNDO)
        cabecalho.grid(row=0, column=0, sticky="ew", pady=(ESPACO, 0))

        linha = tk.Frame(cabecalho, bg=FUNDO)
        linha.pack(anchor="w")

        # Marca oficial (prisma-logo-minimal.svg): mesmo triangulo com
        # aresta central e "V" da base usado no favicon e na landing
        # (frontend/src/components/ui/Logo.tsx), redesenhado aqui porque
        # o Tk nao importa SVG - so sabe desenhar linha e poligono.
        marca = tk.Canvas(linha, width=42, height=42, bg=FUNDO, highlightthickness=0)
        marca.pack(side="left")
        desenhar_logo_prisma(marca, TEXTO, tamanho=42)

        tk.Label(
            linha, text="PRISMA", font=self.fontes["marca"], bg=FUNDO, fg=TEXTO,
        ).pack(side="left", padx=(14, 0))

        tk.Label(
            cabecalho,
            text="Plataforma de estudos com IA",
            font=self.fontes["subtitulo"],
            bg=FUNDO,
            fg=TEXTO_TENUE,
        ).pack(anchor="w", pady=(3, 0))

    def _secao(self, titulo: str, linha: int) -> tk.Frame:
        """Cria um bloco rotulado na coluna central.

        Devolve o Frame onde a secao se monta. O rotulo e o conteudo
        ficam juntos para que a linha do grid represente a secao inteira.
        """
        bloco = tk.Frame(self.coluna, bg=FUNDO)
        bloco.grid(row=linha, column=0, sticky="nsew", pady=(ESPACO, 0))
        bloco.columnconfigure(0, weight=1)
        bloco.rowconfigure(1, weight=1)

        tk.Label(
            bloco, text=titulo.upper(), font=self.fontes["secao"],
            bg=FUNDO, fg=TEXTO_TENUE,
        ).grid(row=0, column=0, sticky="w", pady=(0, 9))
        return bloco

    def _montar_status(self) -> None:
        bloco = self._secao("Status", 1)

        cartao = tk.Frame(
            bloco, bg=SUPERFICIE,
            highlightbackground=BORDA, highlightthickness=1,
        )
        cartao.grid(row=1, column=0, sticky="ew")

        self.linhas: dict[str, LinhaStatus] = {}
        rotulos = ("Servidor", "Dependências", "Telas da aplicação", "npm", "Porta")
        for indice, rotulo in enumerate(rotulos):
            if indice:
                # Divisoria suave, nunca linha de tabela.
                tk.Frame(cartao, bg=BORDA, height=1).pack(fill="x", padx=22)
            self.linhas[rotulo] = LinhaStatus(cartao, rotulo, self.fontes)

        tk.Frame(cartao, bg=SUPERFICIE, height=6).pack(fill="x")

    def _montar_acoes(self) -> None:
        bloco = self._secao("Ações", 2)

        grade = tk.Frame(bloco, bg=FUNDO)
        grade.grid(row=1, column=0, sticky="ew")
        grade.columnconfigure((0, 1), weight=1, uniform="cards")

        # (chave, icone, titulo, descricao, callback, primario)
        acoes = [
            ("servidor", ICONES["rodar"], "Rodar servidor", "Inicia o Vite", self.acao_servidor, True),
            ("abrir", ICONES["navegador"], "Abrir navegador", "Abre a landing page", self.acao_abrir, False),
            ("instalar", ICONES["pacote"], "Instalar dependências", "Executa npm install", self.acao_instalar, False),
            ("sincronizar", ICONES["sincronizar"], "Sincronizar", "Atualiza as telas", self.acao_sincronizar, False),
            ("build", ICONES["build"], "Build", "Compila produção", self.acao_build, False),
            ("validar", ICONES["validar"], "Validar", "Executa lint e build", self.acao_validar, False),
            ("porta", ICONES["porta"], "Porta", f"Atual: {self.porta}", self.acao_configurar, False),
            ("limpar", ICONES["limpar"], "Limpar console", "Esvazia a saída", self.acao_limpar, False),
        ]

        for indice, (chave, icone, titulo, desc, callback, primario) in enumerate(acoes):
            card = CardAcao(grade, icone, titulo, desc, callback, self.fontes, primario)
            card.canvas.grid(
                row=indice // 2,
                column=indice % 2,
                sticky="ew",
                padx=(0, 7) if indice % 2 == 0 else (7, 0),
                pady=4,
            )
            self.cards[chave] = card

    def _montar_console(self) -> None:
        bloco = tk.Frame(self.coluna, bg=FUNDO)
        bloco.grid(row=3, column=0, sticky="nsew", pady=(ESPACO, ESPACO))
        bloco.columnconfigure(0, weight=1)
        bloco.rowconfigure(1, weight=1)

        topo = tk.Frame(bloco, bg=FUNDO)
        topo.grid(row=0, column=0, sticky="ew", pady=(0, 9))
        tk.Label(
            topo, text="▍ CONSOLE", font=self.fontes["secao"], bg=FUNDO, fg=TEXTO_TENUE,
        ).pack(side="left")
        self.rotulo_pasta = tk.Label(
            topo, text="~", font=self.fontes["dica"], bg=FUNDO, fg=TEXTO_TENUE,
        )
        self.rotulo_pasta.pack(side="right")
        tk.Label(
            topo, text="Enter executa  ·  ", font=self.fontes["dica"],
            bg=FUNDO, fg=TEXTO_TENUE,
        ).pack(side="right")

        # `pack_propagate(False)` + altura minima garantem que o console
        # nunca seja espremido a zero por falta de espaco: sem isso, numa
        # tela mais baixa a grade de acoes come a area toda e sobra so o
        # rotulo "CONSOLE".
        moldura = tk.Frame(bloco, bg=CONSOLE_FUNDO, height=ALTURA_CONSOLE)
        moldura.grid(row=1, column=0, sticky="nsew")
        moldura.pack_propagate(False)

        # A entrada e empacotada ANTES da area de saida, embora apareca
        # embaixo: o `pack` serve os primeiros widgets primeiro, e quem
        # pede `expand=True` fica com o resto. Na ordem inversa a area de
        # saida engolia tudo e a linha de comando ficava com 1px.
        self._montar_entrada(moldura)

        # Area de saida + barra de rolagem desenhada.
        area = tk.Frame(moldura, bg=CONSOLE_FUNDO)
        area.pack(fill="both", expand=True, side="top")

        self.console = tk.Text(
            area,
            font=self.fontes["console"],
            bg=CONSOLE_FUNDO,
            fg=CONSOLE_TEXTO,
            insertbackground=CONSOLE_TEXTO,
            selectbackground="#33413a",
            selectforeground="#ffffff",
            relief="flat",
            wrap="word",
            padx=18,
            pady=14,
            bd=0,
            highlightthickness=0,
        )
        self.console.pack(side="left", fill="both", expand=True)

        self.rolagem = BarraRolagem(area, self.console)
        self.rolagem.canvas.pack(side="right", fill="y", padx=(0, 7), pady=10)

        self.console.tag_config("ok", foreground=CONSOLE_OK)
        self.console.tag_config("erro", foreground=CONSOLE_ERRO)
        self.console.tag_config("suave", foreground=CONSOLE_SUAVE)
        self.console.tag_config("comando", foreground=CONSOLE_COMANDO)

        # Somente leitura para digitacao, mas ainda selecionavel e
        # copiavel: `state="disabled"` no Tk ja permite selecionar. O que
        # se digita vai para a linha de entrada abaixo, nao aqui.
        self.console.config(state="disabled")
        self.console.bind("<Button-1>", lambda _e: self.entrada.focus_set())

        self._atualizar_prompt()
        self._escrever("Pronto para começar. Digite 'help' para os comandos.", "suave")

    def _montar_entrada(self, pai: tk.Widget) -> None:
        """Linha de comando do console."""
        linha = tk.Frame(pai, bg=CONSOLE_ENTRADA)
        linha.pack(fill="x", side="bottom")

        tk.Label(
            linha, text="❯", font=self.fontes["console_prompt"],
            bg=CONSOLE_ENTRADA, fg=CONSOLE_OK, padx=0,
        ).pack(side="left", padx=(18, 8), pady=10)

        self.entrada = tk.Entry(
            linha,
            font=self.fontes["console"],
            bg=CONSOLE_ENTRADA,
            fg=CONSOLE_TEXTO,
            insertbackground=CONSOLE_TEXTO,
            relief="flat",
            bd=0,
            highlightthickness=0,
        )
        self.entrada.pack(side="left", fill="x", expand=True, padx=(0, 18), pady=10)

        self.entrada.bind("<Return>", self._enviar_comando)
        self.entrada.bind("<Up>", self._historico_anterior)
        self.entrada.bind("<Down>", self._historico_seguinte)
        self.entrada.bind("<Control-c>", self._interromper)

    def _ajustar_altura(self) -> None:
        """Dimensiona a janela pelo que o conteudo pede.

        As secoes de cima tem altura fixa; so o console estica. Se a
        janela abrir menor que a soma delas, o grid tira o que falta
        justamente do console - foi o que deixava a linha de comando
        espremida. Aqui a altura sai do `reqheight` real, limitada pela
        tela para nao abrir uma janela maior que o monitor.
        """
        self.raiz.update_idletasks()

        preciso = self.coluna.winfo_reqheight() + 2 * ESPACO
        disponivel = int(self.raiz.winfo_screenheight() * 0.9)
        altura = min(preciso, disponivel)
        largura = max(980, self.coluna.winfo_reqwidth() + 2 * ESPACO)

        self.raiz.geometry(f"{largura}x{altura}")
        # Minimo: tudo que e fixo, mais um console utilizavel.
        fixo = preciso - ALTURA_CONSOLE
        self.raiz.minsize(820, min(disponivel, fixo + 160))

    def _surgir(self) -> None:
        """Fade-in ao abrir: o Tk so permite alpha na janela inteira."""
        self.raiz.attributes("-alpha", 0.0)

        def passo(valor: float) -> None:
            self.raiz.attributes("-alpha", min(1.0, valor))
            if valor < 1.0:
                self.raiz.after(16, lambda: passo(valor + 0.12))

        passo(0.0)
