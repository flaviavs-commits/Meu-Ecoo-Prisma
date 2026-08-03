from config.settings import prod


def test_producao_permite_credenciais_cors_para_refresh_cookie():
    assert prod.CORS_ALLOW_CREDENTIALS is True


def test_producao_isenta_health_check_do_redirect_tls_interno():
    assert prod.SECURE_REDIRECT_EXEMPT == [r"^api/v1/health/$"]
