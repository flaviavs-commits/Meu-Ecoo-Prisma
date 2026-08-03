def test_rota_inexistente_responde_no_formato_do_contrato(client):
    resposta = client.get("/api/v1/rota-que-nao-existe/")

    assert resposta.status_code == 404
    corpo = resposta.json()
    assert "erro" in corpo
    assert corpo["erro"]["codigo"] == "nao_encontrado"
    assert "mensagem" in corpo["erro"]


def test_metodo_nao_permitido_passa_pelo_handler_unico_do_drf(client):
    resposta = client.post("/api/v1/health/")

    assert resposta.status_code == 405
    corpo = resposta.json()
    assert corpo["erro"]["codigo"] == "metodo_nao_permitido"
