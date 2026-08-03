"""Leitura do estado do ambiente: npm, dependencias, telas e porta.

Sao as perguntas que o card de status faz a cada ciclo. Nenhuma delas
toca a interface - por isso podem rodar em thread.
"""

from __future__ import annotations

import csv
import io
import re
import shutil
import socket
import subprocess
import sys
from dataclasses import dataclass
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


def pids_na_porta(porta: int) -> list[int]:
    """Lista os PIDs escutando na porta especifica."""
    return [item.pid for item in portas_em_escuta() if item.porta == porta]


@dataclass(frozen=True)
class PortaEmUso:
    """Uma porta TCP em LISTENING, com o processo dono dela."""

    porta: int
    pid: int
    processo: str
    projeto: str


def _nomes_processos() -> dict[int, str]:
    """Mapeia PID -> nome do executavel, via `tasklist` (formato CSV)."""
    try:
        saida = subprocess.run(
            ["tasklist", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return {}

    nomes: dict[int, str] = {}
    for linha in csv.reader(io.StringIO(saida.stdout)):
        if len(linha) < 2:
            continue
        nome, pid = linha[0], linha[1]
        if pid.isdigit():
            nomes[int(pid)] = nome
    return nomes


def _linhas_de_comando(pids: list[int]) -> dict[int, str]:
    """Mapeia PID -> linha de comando completa, via PowerShell/CIM.

    Uma chamada so para todos os PIDs, nao uma por processo: abrir um
    PowerShell por porta deixaria o painel visivelmente lento com varias
    portas abertas. `wmic` (a alternativa mais direta) foi removido a
    partir do Windows 11 24H2; `Get-CimInstance Win32_Process` e o
    substituto oficial da Microsoft.

    A linha de comando e o que costuma denunciar o projeto: `node
    .../frontend/node_modules/vite/bin/vite.js` ou `python
    .../scripts/hud.py`, por exemplo - coisa que o nome do processo
    sozinho ("node.exe", "python.exe") nao diz.
    """
    if not pids:
        return {}

    filtro = " or ".join(f"ProcessId={pid}" for pid in pids)
    comando = (
        f"Get-CimInstance Win32_Process -Filter '{filtro}' "
        "| ForEach-Object { \"$($_.ProcessId)`t$($_.CommandLine)\" }"
    )
    try:
        saida = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", comando],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return {}

    linhas_de_comando: dict[int, str] = {}
    for linha in saida.stdout.splitlines():
        pid_texto, _, comando_linha = linha.partition("\t")
        if pid_texto.isdigit():
            linhas_de_comando[int(pid_texto)] = comando_linha.strip()
    return linhas_de_comando


def _projeto_da_linha_de_comando(linha_de_comando: str) -> str:
    """Reduz a linha de comando a um pedaco curto que identifique o projeto.

    Pega o ultimo trecho de caminho reconhecivel (pasta antes de
    node_modules, ou o script/arquivo executado) em vez da linha inteira,
    que costuma ter flags demais para caber num card.
    """
    if not linha_de_comando:
        return ""

    partes = linha_de_comando.replace("\\", "/").split("/node_modules/")
    if len(partes) > 1:
        # ".../Estudo-com-IA/frontend/node_modules/vite/bin/vite.js"
        # -> "Estudo-com-IA/frontend"
        base = partes[0].rstrip("/").split("/")
        return "/".join(base[-2:]) if len(base) > 1 else base[-1]

    # Sem node_modules: usa o ultimo argumento com barra (o script/arquivo).
    candidatos = [p for p in linha_de_comando.split() if "/" in p or "\\" in p]
    if candidatos:
        alvo = candidatos[-1].replace("\\", "/").split("/")
        return "/".join(alvo[-2:]) if len(alvo) > 1 else alvo[-1]

    return linha_de_comando[:40]


def portas_em_escuta() -> list[PortaEmUso]:
    """Lista as portas TCP em LISTENING nesta maquina, com dono e projeto.

    No Windows usa `netstat`/PowerShell. No macOS/Linux usa `lsof` quando
    disponivel, mantendo o painel funcional sem depender de psutil.
    """
    if sys.platform != "win32":
        return _portas_posix()

    try:
        saida = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return []

    brutos: dict[int, int] = {}  # porta -> pid (uma porta, um listener)
    for linha in saida.stdout.splitlines():
        partes = linha.split()
        if len(partes) < 5 or partes[0] not in ("TCP", "TCP6"):
            continue
        endereco_local, estado, pid = partes[1], partes[3], partes[-1]
        if estado != "LISTENING" or not pid.isdigit():
            continue
        try:
            porta = int(endereco_local.rsplit(":", 1)[-1])
        except ValueError:
            continue
        brutos[porta] = int(pid)

    if not brutos:
        return []

    nomes = _nomes_processos()
    linhas_de_comando = _linhas_de_comando(sorted(set(brutos.values())))
    resultado = []
    for porta, pid in sorted(brutos.items()):
        processo = nomes.get(pid, "desconhecido")
        projeto = _projeto_da_linha_de_comando(linhas_de_comando.get(pid, ""))
        resultado.append(PortaEmUso(porta, pid, processo, projeto))
    return resultado


def _portas_posix() -> list[PortaEmUso]:
    """Lista listeners POSIX com lsof, sem presumir nomes de processos."""
    try:
        saida = subprocess.run(
            ["lsof", "-nP", "-iTCP", "-sTCP:LISTEN", "-F", "pcn"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return []

    processo = "desconhecido"
    pid = None
    resultado: dict[tuple[int, int], PortaEmUso] = {}
    porta_re = re.compile(r":(\d+)$")
    for linha in saida.stdout.splitlines():
        if linha.startswith("p"):
            pid = int(linha[1:]) if linha[1:].isdigit() else None
        elif linha.startswith("c"):
            processo = linha[1:] or "desconhecido"
        elif linha.startswith("n") and pid is not None:
            encontrado = porta_re.search(linha[1:])
            if encontrado:
                porta = int(encontrado.group(1))
                resultado[(porta, pid)] = PortaEmUso(
                    porta, pid, processo, _projeto_da_linha_de_comando(linha[1:])
                )
    return sorted(resultado.values(), key=lambda item: (item.porta, item.pid))
