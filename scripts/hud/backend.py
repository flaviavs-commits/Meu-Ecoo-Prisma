"""Ciclo de vida da API Django local no HUD.

Totalmente independente do frontend: o card principal ('Rodar
aplicacao') nunca chama nada daqui. Quem quiser a API sobe pelo card
'Rodar backend', a parte.
"""

from __future__ import annotations

import os
import subprocess
import sys
import threading
from pathlib import Path

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

    def _venv_tem_dependencias(self, venv: Path) -> bool:
        """Diz se o venv ja recebeu `pip install`.

        Olha o disco em vez de rodar um subprocesso: a checagem acontece
        a cada clique e nao pode custar o tempo de subir um Python.
        Confere o Django, que e a dependencia da qual o resto depende.
        """
        pastas = (
            venv / "Lib" / "site-packages",
            *(venv / "lib").glob("python*/site-packages"),
        )
        return any((pasta / "django").is_dir() for pasta in pastas)

    def _pendencias_backend(self) -> list[str]:
        """Aponta o que falta montar no ambiente local, antes de tentar.

        Sem isso o `migrate` falha por import e o console so mostra um
        traceback de Python, que nao diz o que fazer.
        """
        pendencias: list[str] = []
        venv = BACKEND / ".venv"
        if not venv.is_dir():
            pendencias.append(
                "Falta o ambiente virtual do backend. Rode:  "
                "cd backend && python -m venv .venv && "
                ".venv/Scripts/python -m pip install -r requirements.txt"
            )
        elif not self._venv_tem_dependencias(venv):
            # Um `python -m venv` sem o `pip install` deixa a pasta no
            # lugar, entao a checagem acima passa e o erro so apareceria
            # no traceback do migrate.
            pendencias.append(
                "O ambiente virtual do backend esta vazio. Rode:  "
                "cd backend && .venv/Scripts/python -m pip install -r requirements.txt"
            )
        if not (BACKEND / ".env").is_file():
            pendencias.append(
                "Falta backend/.env. Copie o backend/.env.example e preencha "
                "DJANGO_SECRET_KEY (o resto tem padrao de desenvolvimento)."
            )
        return pendencias

    def _explicar_falha(self, saida: str) -> str:
        """Traduz as falhas conhecidas do backend para uma acao concreta."""
        if "No module named" in saida:
            return (
                "As dependencias do backend nao estao instaladas. Rode:  "
                "cd backend && .venv/Scripts/python -m pip install -r requirements.txt"
            )
        if "DJANGO_SECRET_KEY" in saida:
            return "Defina DJANGO_SECRET_KEY em backend/.env (veja backend/.env.example)."
        if "DATABASE_URL" in saida:
            return "Defina DATABASE_URL em backend/.env (veja backend/.env.example)."
        return ""

    def _backend_env(self) -> dict[str, str]:
        ambiente = os.environ.copy()
        banco = ambiente.get("PRISMA_LOCAL_DATABASE_URL")
        if not banco:
            banco = f"sqlite:///{(BACKEND / 'local-dev.sqlite3').as_posix()}"
        ambiente["DATABASE_URL"] = banco
        ambiente.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
        return ambiente

    def _subir_backend(self) -> None:
        if not (BACKEND / "manage.py").is_file():
            self._escrever("Backend nao encontrado em backend/manage.py.", "erro")
            self._toast_mostrar("Backend ausente", False)
            return
        if porta_em_uso(self.porta_backend):
            self._escrever(f"A porta do backend ({self.porta_backend}) ja esta em uso.", "erro")
            self._toast_mostrar("Porta do backend ocupada", False)
            return

        pendencias = self._pendencias_backend()
        if pendencias:
            for pendencia in pendencias:
                self._escrever(pendencia, "erro")
            self._toast_mostrar("Ambiente do backend incompleto", False)
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
                # Sem o stderr, a causa (import quebrado, variavel de
                # ambiente ausente) fica invisivel e sobra so o toast.
                for linha in migracao.stderr.splitlines():
                    self.fila.put(("", linha.rstrip()))
                pista = self._explicar_falha(migracao.stderr)
                if pista:
                    self.fila.put(("erro", pista))
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
