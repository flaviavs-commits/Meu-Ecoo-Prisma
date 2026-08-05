"""Ambiente de desenvolvimento: DEBUG on, CORS liberado para a SPA local."""

from .base import *  # noqa: F401,F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Sem manifesto: em dev o runserver serve estatico direto dos apps via
# finders, sem precisar rodar collectstatic a cada alteracao de CSS/JS.
STORAGES = {
    **STORAGES,
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

CORS_ALLOWED_ORIGINS = sorted(
    set(CORS_ALLOWED_ORIGINS)
    | {
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    }
)
CORS_ALLOW_CREDENTIALS = True
