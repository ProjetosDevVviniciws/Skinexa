from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest
import requests

from skinexa.integrations.bcb.client import (
    BCBIndisponivel,
    CotacaoBCBNaoEncontrada,
    RespostaBCBInvalida,
    buscar_cotacao_usd_brl,
)

@patch(
    "skinexa.integrations.bcb.client."
    "requests.get",
)

def test_buscar_cotacao_usd_brl_com_sucesso(
    mock_get,
    app,
):
    """Testa uma consulta válida da cotação USD/BRL."""

    resposta = Mock()

    resposta.status_code = 200
    resposta.raise_for_status.return_value = None

    resposta.json.return_value = {
        "value": [
            {
                "cotacaoCompra": 5.31,
                "cotacaoVenda": 5.32,
                "dataHoraCotacao": (
                    "2026-09-11 13:10:00.000"
                ),
                "tipoBoletim": "Fechamento",
            }
        ]
    }

    mock_get.return_value = resposta

    with app.app_context():
        resultado = buscar_cotacao_usd_brl()

    assert resultado.moeda_origem == "USD"
    assert resultado.moeda_destino == "BRL"

    assert resultado.taxa == Decimal("5.32")

    assert resultado.cotado_em == datetime(
        2026,
        9,
        11,
        13,
        10,
    )

@patch(
    "skinexa.integrations.bcb.client."
    "requests.get",
)

def test_buscar_cotacao_usd_brl_usa_fechamento_mais_recente(
    mock_get,
    app,
):
    """Testa a seleção do fechamento mais recente."""

    resposta = Mock()

    resposta.status_code = 200
    resposta.raise_for_status.return_value = None

    resposta.json.return_value = {
        "value": [
            {
                "cotacaoVenda": 5.20,
                "dataHoraCotacao": (
                    "2026-09-10 13:10:00.000"
                ),
                "tipoBoletim": "Fechamento",
            },
            {
                "cotacaoVenda": 5.35,
                "dataHoraCotacao": (
                    "2026-09-11 13:10:00.000"
                ),
                "tipoBoletim": "Fechamento",
            },
        ]
    }

    mock_get.return_value = resposta

    with app.app_context():
        resultado = buscar_cotacao_usd_brl()

    assert resultado.taxa == Decimal("5.35")

    assert resultado.cotado_em == datetime(
        2026,
        9,
        11,
        13,
        10,
    )

@patch(
    "skinexa.integrations.bcb.client."
    "requests.get",
)

def test_buscar_cotacao_usd_brl_ignora_boletim_intermediario(
    mock_get,
    app,
):
    """Testa se boletins intermediários são ignorados."""

    resposta = Mock()

    resposta.status_code = 200
    resposta.raise_for_status.return_value = None

    resposta.json.return_value = {
        "value": [
            {
                "cotacaoVenda": 5.50,
                "dataHoraCotacao": (
                    "2026-09-11 12:00:00.000"
                ),
                "tipoBoletim": "Intermediário",
            },
            {
                "cotacaoVenda": 5.30,
                "dataHoraCotacao": (
                    "2026-09-11 13:10:00.000"
                ),
                "tipoBoletim": "Fechamento",
            },
        ]
    }

    mock_get.return_value = resposta

    with app.app_context():
        resultado = buscar_cotacao_usd_brl()

    assert resultado.taxa == Decimal("5.30")

@patch(
    "skinexa.integrations.bcb.client."
    "requests.get",
)

def test_identificar_bcb_indisponivel(
    mock_get,
    app,
):
    """Testa tratamento de erro interno do Banco Central."""

    resposta = Mock()
    resposta.status_code = 500

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            BCBIndisponivel,
        ):
            buscar_cotacao_usd_brl()

@patch(
    "skinexa.integrations.bcb.client."
    "requests.get",
)

def test_tratar_timeout_bcb(
    mock_get,
    app,
):
    """Testa tratamento de timeout do Banco Central."""

    mock_get.side_effect = requests.Timeout

    with app.app_context():
        with pytest.raises(
            BCBIndisponivel,
        ):
            buscar_cotacao_usd_brl()

@patch(
    "skinexa.integrations.bcb.client."
    "requests.get",
)

def test_tratar_erro_conexao_bcb(
    mock_get,
    app,
):
    """Testa tratamento de erro de conexão."""

    mock_get.side_effect = (
        requests.RequestException()
    )

    with app.app_context():
        with pytest.raises(
            BCBIndisponivel,
        ):
            buscar_cotacao_usd_brl()

@patch(
    "skinexa.integrations.bcb.client."
    "requests.get",
)

def test_rejeitar_json_invalido_bcb(
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
            RespostaBCBInvalida,
        ):
            buscar_cotacao_usd_brl()

@patch(
    "skinexa.integrations.bcb.client."
    "requests.get",
)

def test_rejeitar_resposta_que_nao_seja_objeto_bcb(
    mock_get,
    app,
):
    """Testa rejeição de estrutura principal inválida."""

    resposta = Mock()

    resposta.status_code = 200
    resposta.raise_for_status.return_value = None

    resposta.json.return_value = []

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            RespostaBCBInvalida,
            match="não é um objeto JSON",
        ):
            buscar_cotacao_usd_brl()

@patch(
    "skinexa.integrations.bcb.client."
    "requests.get",
)

def test_rejeitar_value_invalido_bcb(
    mock_get,
    app,
):
    """Testa rejeição de lista de cotações inválida."""

    resposta = Mock()

    resposta.status_code = 200
    resposta.raise_for_status.return_value = None

    resposta.json.return_value = {
        "value": {
            "cotacaoVenda": 5.30,
        }
    }

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            RespostaBCBInvalida,
            match="lista de cotações válida",
        ):
            buscar_cotacao_usd_brl()

@patch(
    "skinexa.integrations.bcb.client."
    "requests.get",
)

def test_rejeitar_ausencia_de_fechamento_bcb(
    mock_get,
    app,
):
    """Testa ausência de boletim de fechamento."""

    resposta = Mock()

    resposta.status_code = 200
    resposta.raise_for_status.return_value = None

    resposta.json.return_value = {
        "value": [
            {
                "cotacaoVenda": 5.30,
                "dataHoraCotacao": (
                    "2026-09-11 12:00:00.000"
                ),
                "tipoBoletim": "Intermediário",
            }
        ]
    }

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            CotacaoBCBNaoEncontrada,
            match="Nenhuma cotação de fechamento",
        ):
            buscar_cotacao_usd_brl()

@patch(
    "skinexa.integrations.bcb.client."
    "requests.get",
)

def test_rejeitar_cotacao_invalida_bcb(
    mock_get,
    app,
):
    """Testa rejeição de cotação monetária inválida."""

    resposta = Mock()

    resposta.status_code = 200
    resposta.raise_for_status.return_value = None

    resposta.json.return_value = {
        "value": [
            {
                "cotacaoVenda": "invalida",
                "dataHoraCotacao": (
                    "2026-09-11 13:10:00.000"
                ),
                "tipoBoletim": "Fechamento",
            }
        ]
    }

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            RespostaBCBInvalida,
            match="cotação inválida",
        ):
            buscar_cotacao_usd_brl()

@patch(
    "skinexa.integrations.bcb.client."
    "requests.get",
)

def test_rejeitar_cotacao_zero_bcb(
    mock_get,
    app,
):
    """Testa rejeição de cotação igual a zero."""

    resposta = Mock()

    resposta.status_code = 200
    resposta.raise_for_status.return_value = None

    resposta.json.return_value = {
        "value": [
            {
                "cotacaoVenda": 0,
                "dataHoraCotacao": (
                    "2026-09-11 13:10:00.000"
                ),
                "tipoBoletim": "Fechamento",
            }
        ]
    }

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            RespostaBCBInvalida,
            match="cotação inválida",
        ):
            buscar_cotacao_usd_brl()

@patch(
    "skinexa.integrations.bcb.client."
    "requests.get",
)

def test_rejeitar_data_invalida_bcb(
    mock_get,
    app,
):
    """Testa rejeição de data de cotação inválida."""

    resposta = Mock()

    resposta.status_code = 200
    resposta.raise_for_status.return_value = None

    resposta.json.return_value = {
        "value": [
            {
                "cotacaoVenda": 5.30,
                "dataHoraCotacao": "data-invalida",
                "tipoBoletim": "Fechamento",
            }
        ]
    }

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            RespostaBCBInvalida,
            match="data de cotação inválida",
        ):
            buscar_cotacao_usd_brl()

@patch(
    "skinexa.integrations.bcb.client."
    "requests.get",
)

def test_rejeitar_fechamento_sem_data_bcb(
    mock_get,
    app,
):
    """Testa fechamento sem data utilizável."""

    resposta = Mock()

    resposta.status_code = 200
    resposta.raise_for_status.return_value = None

    resposta.json.return_value = {
        "value": [
            {
                "cotacaoVenda": 5.30,
                "dataHoraCotacao": None,
                "tipoBoletim": "Fechamento",
            }
        ]
    }

    mock_get.return_value = resposta

    with app.app_context():
        with pytest.raises(
            CotacaoBCBNaoEncontrada,
            match="possui data válida",
        ):
            buscar_cotacao_usd_brl()