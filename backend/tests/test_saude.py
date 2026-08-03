def test_health_check_responde_ok(client):
    resposta = client.get("/api/v1/health/")

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}
