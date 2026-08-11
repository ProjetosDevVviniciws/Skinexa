def test_erro_404_html(client):
    """Testa a resposta de erro 404 em HTML."""
    resposta = client.get(
        "/rota-que-nao-existe"
    )

    assert resposta.status_code == 404

    conteudo = resposta.get_data(
        as_text=True
    )

    assert "Página não encontrada" in conteudo
    
def test_erro_404_json(client):
    """Testa a resposta de erro 404 em JSON."""
    resposta = client.get(
        "/rota-que-nao-existe",
        headers={
            "Accept": "application/json",
        },
    )

    assert resposta.status_code == 404
    assert resposta.is_json

    dados = resposta.get_json()

    assert dados["sucesso"] is False

    assert (
        dados["mensagem"]
        == "O recurso solicitado não foi encontrado."
    )
    
def test_erro_interno_html(app, client):
    """Testa a resposta de erro 500 em HTML."""
    @app.get("/teste-erro-interno")
    def teste_erro():
        raise RuntimeError(
            "Erro proposital para teste."
        )

    resposta = client.get(
        "/teste-erro-interno"
    )

    assert resposta.status_code == 500

    conteudo = resposta.get_data(
        as_text=True
    )

    assert (
        "Não foi possível concluir a operação"
        in conteudo
    )

    assert (
        "Erro proposital para teste"
        not in conteudo
    )
    
def test_erro_interno_json(app, client):
    """"Testa a resposta de erro 500 em JSON."""
    @app.get("/teste-erro-json")
    def teste_erro_json():
        raise RuntimeError(
            "Informação interna sensível."
        )

    resposta = client.get(
        "/teste-erro-json",
        headers={
            "Accept": "application/json",
        },
    )

    assert resposta.status_code == 500
    assert resposta.is_json

    dados = resposta.get_json()

    assert dados["sucesso"] is False

    assert (
        dados["mensagem"]
        == (
            "Ocorreu um erro interno. "
            "Tente novamente mais tarde."
        )
    )

    assert (
        "Informação interna sensível"
        not in resposta.get_data(as_text=True)
    )
    
def test_erro_405_json(client):
    """Testa a resposta de erro 405 em JSON."""
    resposta = client.put(
        "/dashboard/sincronizar-inventario",
        headers={
            "Accept": "application/json",
        },
    )

    assert resposta.status_code == 405
    assert resposta.is_json

    dados = resposta.get_json()

    assert dados["sucesso"] is False