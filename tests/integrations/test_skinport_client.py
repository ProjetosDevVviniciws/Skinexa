from decimal import Decimal
from unittest.mock import Mock, patch

import pytest
import requests

from skinexa.integrations.skinport.client import (
    ErroSkinport,
    LimiteSkinportExcedido,
    RespostaSkinportInvalida,
    SkinportIndisponivel,
    buscar_precos_skinport,
)

@patch(
    "skinexa.integrations.skinport.client.requests.get"
)

def test_normalizar_moeda_skinport(
    mock_get,
    app,
):
    """Testa a normalização da moeda informada."""

    resposta = Mock()
    resposta.status_code = 200
    resposta.raise_for_status.return_value = None
    resposta.json.return_value = []

    mock_get.return_value = resposta

    with app.app_context():
        resultado = buscar_precos_skinport(
            moeda=" brl ",
        )

    assert resultado.moeda == "BRL"

    mock_get.assert_called_once_with(
        "https://api.skinport.com/v1/items",
        params={
            "app_id": 730,
            "currency": "BRL",
        },
        timeout=10,
        headers={
            "Accept": "application/json",
            "User-Agent": "Skinexa/1.0",
        },
    )

def test_rejeitar_moeda_invalida_skinport(
    app,
):
    """Testa a rejeição de uma moeda inválida."""

    with app.app_context():
        with pytest.raises(ValueError):
            buscar_precos_skinport(
                moeda="BR",
            )

@patch(
    "skinexa.integrations.skinport.client.requests.get"
)

def test_buscar_precos_skinport_com_sucesso(
    mock_get,
    app,
):
    """Testa uma consulta válida de preços à Skinport."""

    resposta = Mock()
    resposta.status_code = 200
    resposta.raise_for_status.return_value = None
    resposta.json.return_value = [
        {
            "market_hash_name": (
                "AK-47 | Redline (Field-Tested)"
            ),
            "min_price": 145.50,
            "max_price": 230.00,
            "mean_price": 167.30,
            "median_price": 160.00,
            "quantity": 42,
            "updated_at": "2026-09-01T12:30:00Z",
        }
    ]

    mock_get.return_value = resposta

    with app.app_context():
        resultado = buscar_precos_skinport(
            moeda="BRL",
        )

    assert resultado.moeda == "BRL"
    assert len(resultado.itens) == 1

    item = resultado.itens[0]

    assert item.market_hash_name == (
        "AK-47 | Redline (Field-Tested)"
    )
    assert item.currency == "BRL"
    assert item.min_price == Decimal("145.5")
    assert item.max_price == Decimal("230.0")
    assert item.mean_price == Decimal("167.3")
    assert item.median_price == Decimal("160.0")
    assert item.quantity == 42
    assert item.updated_at is not None

@patch(
    "skinexa.integrations.skinport.client.requests.get"
)

def test_identificar_limite_skinport(
    mock_get,
    app,
):
    """Testa o tratamento do limite de requisições."""

    resposta = Mock()
    resposta.status_code = 429

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            LimiteSkinportExcedido
        ):
            buscar_precos_skinport()

@patch(
    "skinexa.integrations.skinport.client.requests.get"
)

def test_identificar_skinport_indisponivel(
    mock_get,
    app,
):
    """Testa o tratamento de erro interno da Skinport."""

    resposta = Mock()
    resposta.status_code = 500

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            SkinportIndisponivel
        ):
            buscar_precos_skinport()

@patch(
    "skinexa.integrations.skinport.client.requests.get"
)

def test_tratar_timeout_skinport(
    mock_get,
    app,
):
    """Testa o tratamento de timeout da Skinport."""

    mock_get.side_effect = requests.Timeout

    with app.app_context():
        with pytest.raises(
            SkinportIndisponivel
        ):
            buscar_precos_skinport()

@patch(
    "skinexa.integrations.skinport.client.requests.get"
)

def test_tratar_erro_conexao_skinport(
    mock_get,
    app,
):
    """Testa o tratamento de erro de conexão."""

    mock_get.side_effect = (
        requests.RequestException()
    )

    with app.app_context():
        with pytest.raises(
            SkinportIndisponivel
        ):
            buscar_precos_skinport()

@patch(
    "skinexa.integrations.skinport.client.requests.get"
)

def test_rejeitar_json_invalido_skinport(
    mock_get,
    app,
):
    """Testa a rejeição de uma resposta sem JSON válido."""

    resposta = Mock()
    resposta.status_code = 200
    resposta.raise_for_status.return_value = None
    resposta.json.side_effect = ValueError

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            RespostaSkinportInvalida
        ):
            buscar_precos_skinport()

@patch(
    "skinexa.integrations.skinport.client.requests.get"
)

def test_rejeitar_resposta_que_nao_seja_lista(
    mock_get,
    app,
):
    """Testa a rejeição de uma estrutura inválida."""

    resposta = Mock()
    resposta.status_code = 200
    resposta.raise_for_status.return_value = None
    resposta.json.return_value = {
        "erro": "resposta inesperada",
    }

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            RespostaSkinportInvalida
        ):
            buscar_precos_skinport()

@patch(
    "skinexa.integrations.skinport.client.requests.get"
)

def test_rejeitar_item_sem_market_hash_name(
    mock_get,
    app,
):
    """Testa a rejeição de item sem nome de mercado."""

    resposta = Mock()
    resposta.status_code = 200
    resposta.raise_for_status.return_value = None
    resposta.json.return_value = [
        {
            "min_price": 100.00,
            "quantity": 10,
        }
    ]

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            RespostaSkinportInvalida
        ):
            buscar_precos_skinport()

@patch(
    "skinexa.integrations.skinport.client.requests.get"
)

def test_rejeitar_preco_invalido_skinport(
    mock_get,
    app,
):
    """Testa a rejeição de um preço inválido."""

    resposta = Mock()
    resposta.status_code = 200
    resposta.raise_for_status.return_value = None
    resposta.json.return_value = [
        {
            "market_hash_name": "AK-47 | Redline",
            "min_price": "invalido",
        }
    ]

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            RespostaSkinportInvalida
        ):
            buscar_precos_skinport()

@patch(
    "skinexa.integrations.skinport.client.requests.get"
)

def test_rejeitar_quantidade_invalida_skinport(
    mock_get,
    app,
):
    """Testa a rejeição de uma quantidade inválida."""

    resposta = Mock()
    resposta.status_code = 200
    resposta.raise_for_status.return_value = None
    resposta.json.return_value = [
        {
            "market_hash_name": "AK-47 | Redline",
            "quantity": "abc",
        }
    ]

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            RespostaSkinportInvalida
        ):
            buscar_precos_skinport()