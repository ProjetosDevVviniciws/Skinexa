from urllib.parse import parse_qs, urlparse

from skinexa.integrations.steam.openid import (
    gerar_url_autenticacao,
)

from skinexa.integrations.steam.openid import (
    ErroAutenticacaoSteam,
    validar_retorno_openid,
)

import pytest

def test_gerar_url_autenticacao(app):
    """Testa se a função gera a URL de autenticação corretamente"""
    with app.app_context():
        url = gerar_url_autenticacao()

    url_analisada = urlparse(url)
    parametros = parse_qs(url_analisada.query)

    assert url_analisada.scheme == "https"
    assert url_analisada.netloc == "steamcommunity.com"

    assert parametros["openid.ns"] == [
        "http://specs.openid.net/auth/2.0"
    ]

    assert parametros["openid.mode"] == [
        "checkid_setup"
    ]

    assert parametros["openid.identity"] == [
        (
            "http://specs.openid.net/auth/2.0/"
            "identifier_select"
        )
    ]
    
def test_rejeitar_retorno_sem_confirmacao(app):
    """Testa se a função rejeita um retorno sem confirmação da Steam"""
    parametros = {
        "openid.mode": "cancel",
    }

    with app.app_context():
        with pytest.raises(ErroAutenticacaoSteam):
            validar_retorno_openid(parametros)
            
def test_rejeitar_claimed_id_invalido(app):
    """Testa se a função rejeita um claimed_id que não seja da Steam"""
    parametros = {
        "openid.mode": "id_res",
        "openid.claimed_id": (
            "https://site-malicioso.example/usuario/123"
        ),
        "openid.identity": (
            "https://site-malicioso.example/usuario/123"
        ),
    }

    with app.app_context():
        with pytest.raises(ErroAutenticacaoSteam):
            validar_retorno_openid(parametros)
            
def test_rejeitar_identidades_diferentes(app):
    """Testa se a função rejeita quando claimed_id e identity são diferentes"""
    parametros = {
        "openid.mode": "id_res",
        "openid.claimed_id": (
            "https://steamcommunity.com/openid/id/"
            "76561198000000001"
        ),
        "openid.identity": (
            "https://steamcommunity.com/openid/id/"
            "76561198000000002"
        ),
    }

    with app.app_context():
        with pytest.raises(ErroAutenticacaoSteam):
            validar_retorno_openid(parametros)