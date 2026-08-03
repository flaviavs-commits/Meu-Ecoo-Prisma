"""Ciclo de vida da API Django local no HUD."""

from __future__ import annotations

import os
import subprocess
import sys
import threading

from .ambiente import porta_em_uso
from .caminhos import BACKEND
from .processos import SAIDA_SUBPROCESSO, encerrar_arvore


class BackendMixin:
    """Prepara SQLite local e controla o processo do backend."""

    def acao_backend(self) -> None:
        if self.ocupado and not self.backend:
            self._escrever("O backend ainda esta sendo preparado.", "suave")
            return
        if self.backend and self.backend.poll() is None:
            self._parar_backend()
        else:
            self._subir_backend()

    def _backend_python(self) -> str:
        candidatos = (
            BACKEND / ".venv" / "Scripts" / "python.exe",
            BACKEND / ".venv" / "bin" / "python",
        )
        for candidato in candidatos:
            if candidato.is_file():
                return str(candidato)
        return sys.executable

    def _backend_env(self) -> dict[str, str]:
        ambiente = os.environ.copy()
        banco = ambiente.get("PRISMA_LOCAL_DATABASE_URL")
        if not banco:
            banco = f"sqlite:///{(BACKEND / 'local-dev.sqlite3').as_posix()}"
        ambiente["DATABASE_URL"] = banco
        ambiente.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
        return ambiente

    def _subir_backend(self, iniciar_frontend: bool = False) -> None:
        if not (BACKEND / "manage.py").is_file():
            self._escrever("Backend nao encontrado em backend/manage.py.", "erro")
            self._toast_mostrar("Backend ausente", False)
            return
        if porta_em_uso(self.porta_backend):
            self._escrever(f"A porta do backend ({self.porta_backend}) ja esta em uso.", "erro")
            self._toast_mostrar("Porta do backend ocupada", False)
            return

        self._travar_cards(True)
        self._escrever("Preparando banco SQLite local do backend...", "suave")
        python = self._backend_python()
        ambiente = self._backend_env()

        def trabalho() -> None:
            try:
                migracao = subprocess.run(
                    [python, "manage.py", "migrate", "--noinput"],
                    cwd=BACKEND,
                    env=ambiente,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=120,
                    check=False,
                )
            except (OSError, subprocess.SubprocessError) as exc:
                self.fila.put(("erro", f"Falha ao preparar backend: {exc}"))
                self.fila.put(("fim", ""))
                return

            for linha in migracao.stdout.splitlines():
                self.fila.put(("", linha.rstrip()))
            if migracao.returncode != 0:
                self.fila.put(("erro", "A migracao local do backend falhou."))
                self.fila.put(("toast_erro", "Backend nao foi iniciado"))
                self.fila.put(("fim", ""))
                return

            try:
                self.backend = subprocess.Popen(
                    [python, "manage.py", "runserver", f"127.0.0.1:{self.porta_backend}", "--noreload"],
                    cwd=BACKEND,
                    env=ambiente,
                    **SAIDA_SUBPROCESSO,
                )
            except OSError as exc:
                self.fila.put(("erro", f"Falha ao iniciar backend: {exc}"))
                self.fila.put(("fim", ""))
                return
            self.fila.put(("ok", f"Backend iniciado em http://127.0.0.1:{self.porta_backend}"))
            self.fila.put(("toast_ok", "Backend iniciado"))
            if iniciar_frontend:
                self.fila.put(("backend_pronto", ""))
            else:
                self.fila.put(("fim", ""))

            processo = self.backend
            if processo.stdout is not None:
                for linha in processo.stdout:
                    self.fila.put(("", linha.rstrip()))
            self.fila.put(("suave", "O backend encerrou."))

        threading.Thread(target=trabalho, daemon=True).start()

    def _parar_backend(self) -> None:
        processo = self.backend
        if processo is None or processo.poll() is not None:
            self.backend = None
            return
        self.backend = None
        threading.Thread(target=encerrar_arvore, args=(processo,), daemon=True).start()
