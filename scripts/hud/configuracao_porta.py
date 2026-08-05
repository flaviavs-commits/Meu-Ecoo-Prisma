"""Persistencia da ultima porta escolhida para o frontend do HUD."""

from __future__ import annotations

import json
import os
from pathlib import Path

from .caminhos import PORTA_FRONTEND_MINIMA, PORTA_PADRAO

_NOME_CONFIGURACAO = "prisma-hud.json"


def _arquivo_configuracao() -> Path:
    """Devolve o arquivo de configuracao local da pessoa usuaria."""
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return base / "Prisma" / _NOME_CONFIGURACAO


ARQUIVO_CONFIGURACAO = _arquivo_configuracao()


def _porta_valida(porta: object) -> bool:
    return (
        isinstance(porta, int)
        and not isinstance(porta, bool)
        and PORTA_FRONTEND_MINIMA <= porta <= 65535
    )


def carregar_porta_frontend() -> int:
    """Le a ultima porta salva ou retorna a porta inicial do projeto."""
    try:
        dados = json.loads(ARQUIVO_CONFIGURACAO.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return PORTA_PADRAO

    porta = dados.get("porta_frontend") if isinstance(dados, dict) else None
    return int(porta) if _porta_valida(porta) else PORTA_PADRAO


def salvar_porta_frontend(porta: int) -> bool:
    """Salva a porta escolhida sem deixar configuracao invalida no disco."""
    if not _porta_valida(porta):
        return False

    try:
        ARQUIVO_CONFIGURACAO.parent.mkdir(parents=True, exist_ok=True)
        ARQUIVO_CONFIGURACAO.write_text(
            json.dumps({"porta_frontend": porta}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError:
        return False
    return True
