"""Caminhos do projeto e a porta padrao do servidor de desenvolvimento.

Fica isolado para que qualquer modulo do HUD saiba onde o projeto esta
sem recalcular a raiz nem importar o pacote inteiro.
"""

from __future__ import annotations

from pathlib import Path

# scripts/hud/caminhos.py -> scripts/hud -> scripts -> raiz
RAIZ = Path(__file__).resolve().parent.parent.parent
FRONTEND = RAIZ / "frontend"
BACKEND = RAIZ / "backend"
SINCRONIZAR_APP = RAIZ / "scripts" / "sincronizar-app.py"

PORTA_PADRAO = 5173
PORTA_BACKEND_PADRAO = 8000
