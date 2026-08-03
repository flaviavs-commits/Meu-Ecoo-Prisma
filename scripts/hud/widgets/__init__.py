"""Widgets desenhados do HUD.

Todos existem porque o widget nativo do Tk 8.6 nao aceita canto
arredondado, sombra nem transicao de cor - e era isso que dava ao HUD o
aspecto de formulario antigo. Cada um e um Canvas que se redesenha.
"""

from .barra_rolagem import BarraRolagem
from .botao_modal import BotaoModal
from .card_acao import CardAcao
from .linha_status import LinhaStatus
from .modal import Modal
from .painel_portas import PainelPortas

__all__ = ["BarraRolagem", "BotaoModal", "CardAcao", "LinhaStatus", "Modal", "PainelPortas"]
