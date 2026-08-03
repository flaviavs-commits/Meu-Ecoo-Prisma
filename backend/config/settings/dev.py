"""Ambiente de desenvolvimento: DEBUG on, CORS liberado para a SPA local."""

from .base import *  # noqa: F401,F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

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
