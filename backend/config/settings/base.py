"""Settings comuns a todos os ambientes. Nada de valor sensivel aqui."""

import os
from decimal import Decimal
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "contas",
    "authenticacao",
    "academico",
    "ia",
    "creditos",
    "limites",
    "core",
    "memoria",
    "arquivos",
    "conteudo",
    "aluno",
    "painel_admin",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # "whitenoise.middleware.WhiteNoiseMiddleware" entra so em prod.py:
    # em dev o runserver ja serve estatico via staticfiles, e o Whitenoise
    # avisa (warning) quando STATIC_ROOT/collectstatic ainda nao existe.
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "contas.admin_rate_limit.AdminLoginRateLimitMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

AUTH_USER_MODEL = "contas.Usuario"

# O e-mail é globalmente único para manter o login simples por e-mail e senha.
SILENCED_SYSTEM_CHECKS = ["auth.E003"]

DATABASES = {
    "default": dj_database_url.parse(os.environ["DATABASE_URL"]),
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "media/"
ARQUIVO_MAX_BYTES = int(os.environ.get("ARQUIVO_MAX_BYTES", str(10 * 1024 * 1024)))
ARQUIVO_COTA_INSTITUICAO_BYTES = int(
    os.environ.get("ARQUIVO_COTA_INSTITUICAO_BYTES", str(100 * 1024 * 1024))
)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "EXCEPTION_HANDLER": "core.erros.tratador_de_excecao",
    "DEFAULT_THROTTLE_RATES": {"login": "5/min"},
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]

from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
}

CORS_ALLOWED_ORIGINS = [
    origem
    for origem in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")
    if origem
]

IA_PROVEDOR = os.environ.get("IA_PROVEDOR", "falso")
IA_MODELOS = {
    "TUTORIA": os.environ.get("IA_MODELO_TUTORIA", "modelo-tutoria-local"),
    "GERACAO": os.environ.get("IA_MODELO_GERACAO", "modelo-geracao-local"),
    "CORRECAO": os.environ.get("IA_MODELO_CORRECAO", "modelo-correcao-local"),
    "RESUMO": os.environ.get("IA_MODELO_RESUMO", "modelo-resumo-local"),
}
IA_CUSTO_DOLAR_POR_PERCENTUAL = Decimal(
    os.environ.get("IA_CUSTO_DOLAR_POR_PERCENTUAL", "0.001")
)
IA_MARGEM_USO = Decimal(os.environ.get("IA_MARGEM_USO", "1.20"))
IA_TIMEOUT_SEGUNDOS = float(os.environ.get("IA_TIMEOUT_SEGUNDOS", "10"))
ADMIN_URL = os.environ.get("DJANGO_ADMIN_URL", "backoffice").strip("/") + "/"

# O painel de superadmin (painel_admin) usa @login_required; sem isto o
# Django cai no default "/accounts/login/", que nao existe neste projeto.
LOGIN_URL = "admin:login"
REFRESH_COOKIE_SECURE = os.environ.get("DJANGO_REFRESH_COOKIE_SECURE", "false").lower() == "true"
