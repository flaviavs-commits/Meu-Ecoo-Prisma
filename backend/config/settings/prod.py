"""Ambiente de producao: DEBUG off, hosts restritos, HTTPS forcado."""

import os

from .base import *  # noqa: F401,F403

DEBUG = False
CORS_ALLOW_CREDENTIALS = True

ALLOWED_HOSTS = [
    host
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
    if host
]

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# O health check interno do Railway chega por HTTP antes do proxy TLS.
# As demais rotas continuam obrigadas a usar HTTPS.
SECURE_REDIRECT_EXEMPT = [r"^api/v1/health/$"]
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_AGE = 900
REFRESH_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = [
    origem
    for origem in os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if origem
]
