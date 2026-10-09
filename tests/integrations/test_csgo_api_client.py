from unittest.mock import Mock, patch

import pytest

import requests

from skinexa.integrations.catalogo.csgo_api_client import (
    ErroCSGOAPI,
    buscar_itens_csgo_api,
)

@patch(
    "skinexa.integrations.catalogo."
    "csgo_api_client.requests.get"
)

def test_buscar_itens_csgo_api(
    mock_get,
):
    """Testa uma consulta bem-sucedida."""

    resposta = Mock()
    resposta.json.return_value = [
        {
            "id": "skin-65604_0",
            "market_hash_name": (
                "Desert Eagle | Urban DDPAT "
                "(Factory New)"
            ),
        }
    ]

    mock_get.return_value = resposta

    itens = buscar_itens_csgo_api("skins")

    assert len(itens) == 1

    assert itens[0]["id"] == "skin-65604_0"

    mock_get.assert_called_once_with(
        (
            "https://raw.githubusercontent.com/"
            "ByMykel/CSGO-API/main/public/api/en/"
            "skins_not_grouped.json"
        ),
        timeout=30,
    )

def test_buscar_categoria_invalida():
    """Testa a rejeição de categorias desconhecidas."""

    with pytest.raises(
        ValueError,
        match="Categoria de catálogo não suportada",
    ):
        buscar_itens_csgo_api(
            "categoria_inexistente"
        )

@patch(
    "skinexa.integrations.catalogo."
    "csgo_api_client.requests.get"
)

def test_buscar_itens_erro_http(
    mock_get,
):
    """Testa falhas HTTP da fonte externa."""

    mock_get.side_effect = (
        requests.RequestException(
            "Falha de conexão"
        )
    )

    with pytest.raises(ErroCSGOAPI):
        buscar_itens_csgo_api("skins")

@patch(
    "skinexa.integrations.catalogo."
    "csgo_api_client.requests.get"
)

def test_buscar_itens_resposta_invalida(
    mock_get,
):
    """Testa uma estrutura JSON inesperada."""

    resposta = Mock()
    resposta.json.return_value = {
        "erro": "Resposta inesperada"
    }

    mock_get.return_value = resposta

    with pytest.raises(
        ErroCSGOAPI,
        match="Formato de resposta inválido",
    ):
        buscar_itens_csgo_api("skins")