from urllib.parse import parse_qs, urlparse

def test_login_redireciona_para_steam(client, app):
    """Testa se a rota de login redireciona corretamente para a Steam"""
    resposta = client.get(
        "/auth/steam",
        follow_redirects=False,
    )

    assert resposta.status_code == 302

    url_destino = resposta.headers["Location"]
    url_analisada = urlparse(url_destino)

    assert url_analisada.netloc == "steamcommunity.com"
    assert url_analisada.path == "/openid/login"

    parametros = parse_qs(url_analisada.query)

    assert parametros["openid.mode"] == [
        "checkid_setup"
    ]

    assert parametros["openid.realm"] == [
        app.config["STEAM_OPENID_REALM"]
    ]

    assert parametros["openid.return_to"] == [
        app.config["STEAM_OPENID_RETURN_URL"]
    ]