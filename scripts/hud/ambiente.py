"""Leitura do estado do ambiente: npm, dependencias, telas e porta.

Sao as perguntas que o card de status faz a cada ciclo. Nenhuma delas
toca a interface - por isso podem rodar em thread.
"""

from __future__ import annotations

import shutil
import socket
from functools import lru_cache

from .caminhos import FRONTEND


def npm() -> str | None:
    """Retorna o executavel do npm, ou None se nao estiver no PATH."""
    return _npm_cacheado()


@lru_cache(maxsize=1)
def _npm_cacheado() -> str | None:
    """No Windows o npm e um .cmd, por isso shutil.which.

    Cacheado: o status consulta isso a cada ciclo, e o npm nao aparece
    nem some no meio da sessao.
    """
    return shutil.which("npm")


def dependencias_instaladas() -> bool:
    return (FRONTEND / "node_modules").is_dir()


def app_sincronizada() -> bool:
    """Diz se as telas da aplicacao ja foram trazidas para ca."""
    return (FRONTEND / "public" / "app" / "index.html").is_file()


def porta_em_uso(porta: int) -> bool:
    """Diz se ja ha algo escutando na porta.

    IPv6 vem primeiro de proposito. No Windows, conectar numa porta sem
    listener nao leva RST rapido: gasta o timeout inteiro. Como o Vite
    escuta em `::1`, testar v6 antes resolve o caso comum (servidor no
    ar) em poucos milissegundos, em vez de ~420 ms.

    Com a porta livre, porem, as duas familias gastam o timeout - por
    isso o timeout e curto e quem chama de forma repetida usa uma
    thread (ver `Hud._agendar_status`), nunca o laco do Tkinter.
    """
    for familia, endereco in ((socket.AF_INET6, "::1"), (socket.AF_INET, "127.0.0.1")):
        try:
            with socket.socket(familia, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.25)
                if sock.connect_ex((endereco, porta)) == 0:
                    return True
        except OSError:
            continue
    return False
