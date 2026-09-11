from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest
import requests

from skinexa.integrations.csfloat.client import (
    AutenticacaoCSFloatInvalida,
    CSFloatIndisponivel,
    ErroCSFloat,
    LimiteCSFloatExcedido,
    RespostaCSFloatInvalida,
    buscar_precos_csfloat,
)

@patch(
    "skinexa.integrations.csfloat.client."
    "requests.get",
)

def test_buscar_precos_csfloat_com_sucesso(
    mock_get,
    app,
):
    """Testa uma consulta válida de preços à CSFloat."""

    resposta = Mock()

    resposta.status_code = 200
    resposta.raise_for_status.return_value = None

    resposta.json.return_value = [
        {
            "price": 7518,
            "created_at": (
                "2026-09-07T20:45:13Z"
            ),
            "item": {
                "market_hash_name": (
                    "M4A1-S | Nitro "
                    "(Factory New)"
                ),
            },
        }
    ]

    mock_get.return_value = resposta

    with app.app_context():
        resultado = buscar_precos_csfloat(
            nome_mercado=(
                "M4A1-S | Nitro "
                "(Factory New)"
            ),
        )

    assert resultado.nome_mercado == (
        "M4A1-S | Nitro (Factory New)"
    )

    assert len(resultado.itens) == 1

    item = resultado.itens[0]

    assert item.market_hash_name == (
        "M4A1-S | Nitro (Factory New)"
    )

    assert item.preco == Decimal("75.18")

    assert item.criado_em == datetime(
        2026,
        9,
        7,
        20,
        45,
        13,
    )

    mock_get.assert_called_once_with(
        "https://csfloat.com/api/v1/listings",
        params={
            "market_hash_name": (
                "M4A1-S | Nitro "
                "(Factory New)"
            ),
            "limit": 50,
            "sort_by": "lowest_price",
        },
        timeout=10,
        headers={
            "Accept": "application/json",
            "User-Agent": "Skinexa/1.0",
        },
    )

def test_rejeitar_nome_mercado_vazio_csfloat(
    app,
):
    """Testa rejeição de nome de mercado vazio."""

    with app.app_context():
        with pytest.raises(
            ValueError,
            match="nome de mercado",
        ):
            buscar_precos_csfloat(
                nome_mercado="   ",
            )

def test_rejeitar_limite_menor_que_um_csfloat(
    app,
):
    """Testa rejeição de limite menor que um."""

    with app.app_context():
        with pytest.raises(
            ValueError,
            match="entre 1 e 50",
        ):
            buscar_precos_csfloat(
                nome_mercado="AK-47 | Redline",
                limite=0,
            )

def test_rejeitar_limite_maior_que_cinquenta_csfloat(
    app,
):
    """Testa rejeição de limite maior que cinquenta."""

    with app.app_context():
        with pytest.raises(
            ValueError,
            match="entre 1 e 50",
        ):
            buscar_precos_csfloat(
                nome_mercado="AK-47 | Redline",
                limite=51,
            )

@patch(
    "skinexa.integrations.csfloat.client."
    "requests.get",
)

def test_identificar_limite_csfloat(
    mock_get,
    app,
):
    """Testa o tratamento do limite de requisições."""

    resposta = Mock()
    resposta.status_code = 429

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            LimiteCSFloatExcedido,
        ):
            buscar_precos_csfloat(
                nome_mercado="AK-47 | Redline",
            )

@patch(
    "skinexa.integrations.csfloat.client."
    "requests.get",
)

def test_identificar_csfloat_indisponivel(
    mock_get,
    app,
):
    """Testa o tratamento de erro interno da CSFloat."""

    resposta = Mock()
    resposta.status_code = 500

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            CSFloatIndisponivel,
        ):
            buscar_precos_csfloat(
                nome_mercado="AK-47 | Redline",
            )

@patch(
    "skinexa.integrations.csfloat.client."
    "requests.get",
)

def test_identificar_autenticacao_invalida_csfloat(
    mock_get,
    app,
):
    """Testa rejeição de autenticação pela CSFloat."""

    resposta = Mock()
    resposta.status_code = 401

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            AutenticacaoCSFloatInvalida,
        ):
            buscar_precos_csfloat(
                nome_mercado="AK-47 | Redline",
            )

@patch(
    "skinexa.integrations.csfloat.client."
    "requests.get",
)

def test_tratar_timeout_csfloat(
    mock_get,
    app,
):
    """Testa o tratamento de timeout da CSFloat."""

    mock_get.side_effect = requests.Timeout

    with app.app_context():
        with pytest.raises(
            CSFloatIndisponivel,
        ):
            buscar_precos_csfloat(
                nome_mercado="AK-47 | Redline",
            )

@patch(
    "skinexa.integrations.csfloat.client."
    "requests.get",
)

def test_tratar_erro_conexao_csfloat(
    mock_get,
    app,
):
    """Testa o tratamento de erro de conexão."""

    mock_get.side_effect = (
        requests.RequestException()
    )

    with app.app_context():
        with pytest.raises(
            CSFloatIndisponivel,
        ):
            buscar_precos_csfloat(
                nome_mercado="AK-47 | Redline",
            )

@patch(
    "skinexa.integrations.csfloat.client."
    "requests.get",
)

def test_rejeitar_json_invalido_csfloat(
    mock_get,
    app,
):
    """Testa rejeição de resposta sem JSON válido."""

    resposta = Mock()

    resposta.status_code = 200
    resposta.raise_for_status.return_value = None
    resposta.json.side_effect = ValueError

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            RespostaCSFloatInvalida,
        ):
            buscar_precos_csfloat(
                nome_mercado="AK-47 | Redline",
            )

@patch(
    "skinexa.integrations.csfloat.client."
    "requests.get",
)

def test_rejeitar_resposta_que_nao_seja_lista_csfloat(
    mock_get,
    app,
):
    """Testa rejeição de estrutura inválida."""

    resposta = Mock()

    resposta.status_code = 200
    resposta.raise_for_status.return_value = None

    resposta.json.return_value = {
        "erro": "resposta inesperada",
    }

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            RespostaCSFloatInvalida,
            match="não é uma lista",
        ):
            buscar_precos_csfloat(
                nome_mercado="AK-47 | Redline",
            )

@patch(
    "skinexa.integrations.csfloat.client."
    "requests.get",
)

def test_rejeitar_listing_que_nao_seja_objeto_csfloat(
    mock_get,
    app,
):
    """Testa rejeição de anúncio inválido."""

    resposta = Mock()

    resposta.status_code = 200
    resposta.raise_for_status.return_value = None

    resposta.json.return_value = [
        "listing-invalido"
    ]

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            RespostaCSFloatInvalida,
            match="anúncio inválido",
        ):
            buscar_precos_csfloat(
                nome_mercado="AK-47 | Redline",
            )

@patch(
    "skinexa.integrations.csfloat.client."
    "requests.get",
)

def test_rejeitar_listing_sem_item_csfloat(
    mock_get,
    app,
):
    """Testa rejeição de anúncio sem dados do item."""

    resposta = Mock()

    resposta.status_code = 200
    resposta.raise_for_status.return_value = None

    resposta.json.return_value = [
        {
            "price": 10000,
            "created_at": (
                "2026-09-07T20:45:13Z"
            ),
        }
    ]

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            RespostaCSFloatInvalida,
            match="dados válidos do item",
        ):
            buscar_precos_csfloat(
                nome_mercado="AK-47 | Redline",
            )

@patch(
    "skinexa.integrations.csfloat.client."
    "requests.get",
)

def test_rejeitar_item_sem_market_hash_name_csfloat(
    mock_get,
    app,
):
    """Testa rejeição de item sem nome de mercado."""

    resposta = Mock()

    resposta.status_code = 200
    resposta.raise_for_status.return_value = None

    resposta.json.return_value = [
        {
            "price": 10000,
            "created_at": (
                "2026-09-07T20:45:13Z"
            ),
            "item": {},
        }
    ]

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            RespostaCSFloatInvalida,
            match="market_hash_name",
        ):
            buscar_precos_csfloat(
                nome_mercado="AK-47 | Redline",
            )

@patch(
    "skinexa.integrations.csfloat.client."
    "requests.get",
)

def test_rejeitar_item_diferente_do_solicitado_csfloat(
    mock_get,
    app,
):
    """Testa rejeição de item diferente do solicitado."""

    resposta = Mock()

    resposta.status_code = 200
    resposta.raise_for_status.return_value = None

    resposta.json.return_value = [
        {
            "price": 10000,
            "created_at": (
                "2026-09-07T20:45:13Z"
            ),
            "item": {
                "market_hash_name": (
                    "AWP | Asiimov (Field-Tested)"
                ),
            },
        }
    ]

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            RespostaCSFloatInvalida,
            match="item diferente",
        ):
            buscar_precos_csfloat(
                nome_mercado=(
                    "AK-47 | Redline "
                    "(Field-Tested)"
                ),
            )

@patch(
    "skinexa.integrations.csfloat.client."
    "requests.get",
)

def test_rejeitar_preco_invalido_csfloat(
    mock_get,
    app,
):
    """Testa rejeição de preço que não seja inteiro."""

    resposta = Mock()

    resposta.status_code = 200
    resposta.raise_for_status.return_value = None

    resposta.json.return_value = [
        {
            "price": "7518",
            "created_at": (
                "2026-09-07T20:45:13Z"
            ),
            "item": {
                "market_hash_name": (
                    "AK-47 | Redline"
                ),
            },
        }
    ]

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            RespostaCSFloatInvalida,
            match="preço inválido",
        ):
            buscar_precos_csfloat(
                nome_mercado="AK-47 | Redline",
            )

@patch(
    "skinexa.integrations.csfloat.client."
    "requests.get",
)

def test_rejeitar_preco_negativo_csfloat(
    mock_get,
    app,
):
    """Testa rejeição de preço negativo."""

    resposta = Mock()

    resposta.status_code = 200
    resposta.raise_for_status.return_value = None

    resposta.json.return_value = [
        {
            "price": -100,
            "created_at": (
                "2026-09-07T20:45:13Z"
            ),
            "item": {
                "market_hash_name": (
                    "AK-47 | Redline"
                ),
            },
        }
    ]

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            RespostaCSFloatInvalida,
            match="preço negativo",
        ):
            buscar_precos_csfloat(
                nome_mercado="AK-47 | Redline",
            )

@patch(
    "skinexa.integrations.csfloat.client."
    "requests.get",
)

def test_rejeitar_booleano_como_preco_csfloat(
    mock_get,
    app,
):
    """Testa rejeição de booleano como preço."""

    resposta = Mock()

    resposta.status_code = 200
    resposta.raise_for_status.return_value = None

    resposta.json.return_value = [
        {
            "price": True,
            "created_at": (
                "2026-09-07T20:45:13Z"
            ),
            "item": {
                "market_hash_name": (
                    "AK-47 | Redline"
                ),
            },
        }
    ]

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            RespostaCSFloatInvalida,
            match="preço inválido",
        ):
            buscar_precos_csfloat(
                nome_mercado="AK-47 | Redline",
            )

@patch(
    "skinexa.integrations.csfloat.client."
    "requests.get",
)

def test_rejeitar_data_invalida_csfloat(
    mock_get,
    app,
):
    """Testa rejeição de data inválida."""

    resposta = Mock()

    resposta.status_code = 200
    resposta.raise_for_status.return_value = None

    resposta.json.return_value = [
        {
            "price": 7518,
            "created_at": "data-invalida",
            "item": {
                "market_hash_name": (
                    "AK-47 | Redline"
                ),
            },
        }
    ]

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            RespostaCSFloatInvalida,
            match="data inválida",
        ):
            buscar_precos_csfloat(
                nome_mercado="AK-47 | Redline",
            )

@patch(
    "skinexa.integrations.csfloat.client."
    "requests.get",
)

def test_aceitar_data_ausente_csfloat(
    mock_get,
    app,
):
    """Testa suporte a data ausente."""

    resposta = Mock()

    resposta.status_code = 200
    resposta.raise_for_status.return_value = None

    resposta.json.return_value = [
        {
            "price": 7518,
            "created_at": None,
            "item": {
                "market_hash_name": (
                    "AK-47 | Redline"
                ),
            },
        }
    ]

    mock_get.return_value = resposta

    with app.app_context():
        resultado = buscar_precos_csfloat(
            nome_mercado="AK-47 | Redline",
        )

    assert len(resultado.itens) == 1
    assert resultado.itens[0].criado_em is None

@patch(
    "skinexa.integrations.csfloat.client."
    "requests.get",
)

def test_enviar_api_key_csfloat(
    mock_get,
    app,
):
    """Testa envio opcional da chave da API."""

    resposta = Mock()

    resposta.status_code = 200
    resposta.raise_for_status.return_value = None
    resposta.json.return_value = []

    mock_get.return_value = resposta

    app.config["CSFLOAT_API_KEY"] = (
        "chave-de-teste"
    )

    with app.app_context():
        buscar_precos_csfloat(
            nome_mercado="AK-47 | Redline",
        )

    argumentos = mock_get.call_args

    headers = argumentos.kwargs["headers"]

    assert headers["Authorization"] == (
        "chave-de-teste"
    )