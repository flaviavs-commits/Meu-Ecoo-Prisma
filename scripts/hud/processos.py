"""Como o HUD abre, le e encerra subprocessos.

Concentra o que e especifico de Windows: codepage do console, ausencia
de janela e encerramento por arvore de processos.
"""

from __future__ import annotations

import re
import os
import signal
import subprocess
import sys

# O npm e o Vite colorem a saida com escapes ANSI. No terminal isso vira
# cor; no widget de texto do Tk vira lixo visivel ("<-[32m"). Como o
# console ja tem cor propria por tag, os escapes saem na entrada.
ESCAPES_ANSI = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")


def limpar_ansi(texto: str) -> str:
    """Tira os codigos de cor ANSI de uma linha de saida."""
    return ESCAPES_ANSI.sub("", texto)


# Como os subprocessos sao abertos, em um lugar so.
#   - encoding/errors: o npm imprime caracteres que o console cp1252 do
#     Windows nao aceita; sem isso a leitura estoura.
#   - CREATE_NO_WINDOW: evita um console piscando ao lado da janela.
SAIDA_SUBPROCESSO: dict[str, object] = {
    "stdout": subprocess.PIPE,
    "stderr": subprocess.STDOUT,
    "text": True,
    "encoding": "utf-8",
    "errors": "replace",
    "creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0),
}
if sys.platform != "win32":
    SAIDA_SUBPROCESSO["start_new_session"] = True

# O mesmo, mas em bytes: o console interativo decodifica por conta.
# Ferramentas modernas (npm, git, node) escrevem UTF-8, mas o proprio
# `cmd.exe` responde no codepage OEM (cp850 em portugues) - decodificar
# tudo como UTF-8 transforma "operável" em "oper?vel". Ver `decodificar`.
SAIDA_BYTES: dict[str, object] = {
    "stdout": subprocess.PIPE,
    "stderr": subprocess.STDOUT,
    "creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0),
}
if sys.platform != "win32":
    SAIDA_BYTES["start_new_session"] = True


# Codepage que o shell usa nas mensagens dele. `getpreferredencoding`
# devolve o ANSI (cp1252), que nao serve: o que sai do pipe e o OEM.
def _codepage_oem() -> str:
    if sys.platform != "win32":
        return "utf-8"
    try:
        import ctypes

        return f"cp{ctypes.windll.kernel32.GetOEMCP()}"
    except Exception:  # noqa: BLE001 - sem codepage, o padrao resolve
        return "cp850"


CODEPAGE_SHELL = _codepage_oem()


def decodificar(bruto: bytes) -> str:
    """Decodifica uma linha de saida tentando UTF-8 e caindo no OEM.

    UTF-8 primeiro porque e o que as ferramentas do projeto usam; o
    codepage do console entra so quando a linha nao e UTF-8 valido, que
    e o caso das mensagens do proprio `cmd.exe`.
    """
    try:
        return bruto.decode("utf-8")
    except UnicodeDecodeError:
        return bruto.decode(CODEPAGE_SHELL, errors="replace")


def encerrar_arvore(processo: subprocess.Popen) -> None:
    """Encerra o processo e os filhos dele.

    O `npm run dev` e um wrapper: quem abre a porta e um `node` neto. No
    Windows, `terminate()` mata so o wrapper e deixa o Vite orfao ainda
    segurando a porta - o HUD diria "parado" com o site no ar. Por isso o
    encerramento vai pela arvore inteira (`taskkill /T`).
    """
    if processo.poll() is not None:
        return

    if sys.platform == "win32":
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(processo.pid)],
                capture_output=True,
                timeout=10,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            processo.kill()
    else:
        try:
            os.killpg(processo.pid, signal.SIGTERM)
        except (ProcessLookupError, OSError):
            processo.terminate()

    try:
        processo.wait(timeout=5)
    except subprocess.TimeoutExpired:
        if sys.platform != "win32":
            try:
                os.killpg(processo.pid, signal.SIGKILL)
            except (ProcessLookupError, OSError):
                processo.kill()
        else:
            processo.kill()


def encerrar_pid(pid: int) -> bool:
    """Encerra um PID listado pelo painel usando a API do sistema atual."""
    try:
        if sys.platform == "win32":
            resultado = subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                capture_output=True,
                timeout=10,
                check=False,
            )
            return resultado.returncode == 0
        os.kill(pid, signal.SIGTERM)
        return True
    except (OSError, subprocess.SubprocessError):
        return False
