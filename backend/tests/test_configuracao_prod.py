from config.settings import prod


def test_producao_permite_credenciais_cors_para_refresh_cookie():
    assert prod.CORS_ALLOW_CREDENTIALS is True
