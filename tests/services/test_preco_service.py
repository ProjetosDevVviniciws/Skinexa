from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from skinexa.domain.preco import PrecoMercado
from skinexa.services.precos.service import (
    PlataformaMercadoIndisponivel,
    registrar_precos,
)

def _criar_preco(
    *,
    nome_mercado: str = "AK-47 | Redline (Field-Tested)",
    plataforma: str = "skinport",
) -> PrecoMercado:
    """Cria um preço normalizado para uso nos testes."""

    return PrecoMercado(
        nome_mercado=nome_mercado,
        plataforma=plataforma,
        moeda="BRL",
        menor_preco=Decimal("145.50"),
        maior_preco=Decimal("230.00"),
        preco_medio=Decimal("167.30"),
        preco_mediano=Decimal("160.00"),
        maior_ordem_compra=None,
        quantidade_anuncios=42,
        volume_vendas=None,
        atualizado_na_origem_em=datetime(
            2026,
            9,
            1,
            12,
            30,
        ),
    )

@patch(
    "skinexa.services.precos.service."
    "inserir_historico_preco",
)
@patch(
    "skinexa.services.precos.service."
    "obter_itens_catalogo_ids_por_nomes_mercado",
)
@patch(
    "skinexa.services.precos.service."
    "obter_plataforma_mercado_id_por_identificador",
)

def test_registrar_preco_com_sucesso(
    mock_obter_plataforma,
    mock_obter_itens,
    mock_inserir_historico,
):
    """Testa o registro de um preço normalizado."""

    conexao = Mock()

    mock_obter_plataforma.return_value = 2
    mock_obter_itens.return_value = {
        "AK-47 | Redline (Field-Tested)": 15,
    }
    mock_inserir_historico.return_value = 37

    preco = _criar_preco()

    resultado = registrar_precos(
        conexao,
        [preco],
    )

    assert resultado.total_recebido == 1
    assert resultado.total_registrado == 1
    assert resultado.total_ignorado == 0

    mock_obter_plataforma.assert_called_once_with(
        conexao,
        "skinport",
    )

    mock_obter_itens.assert_called_once_with(
        conexao,
        {
            "AK-47 | Redline (Field-Tested)",
        },
    )

    mock_inserir_historico.assert_called_once_with(
        conexao,
        item_catalogo_id=15,
        plataforma_mercado_id=2,
        moeda="BRL",
        menor_preco=Decimal("145.50"),
        maior_preco=Decimal("230.00"),
        preco_medio=Decimal("167.30"),
        preco_mediano=Decimal("160.00"),
        maior_ordem_compra=None,
        quantidade_anuncios=42,
        volume_vendas=None,
        atualizado_na_origem_em=datetime(
            2026,
            9,
            1,
            12,
            30,
        ),
    )

@patch(
    "skinexa.services.precos.service."
    "inserir_historico_preco",
)
@patch(
    "skinexa.services.precos.service."
    "obter_itens_catalogo_ids_por_nomes_mercado",
)
@patch(
    "skinexa.services.precos.service."
    "obter_plataforma_mercado_id_por_identificador",
)

def test_registrar_preco_ignora_item_inexistente(
    mock_obter_plataforma,
    mock_obter_itens,
    mock_inserir_historico,
):
    """Testa o descarte de item ausente no catálogo."""

    conexao = Mock()

    mock_obter_plataforma.return_value = 2
    mock_obter_itens.return_value = {}

    resultado = registrar_precos(
        conexao,
        [_criar_preco()],
    )

    assert resultado.total_recebido == 1
    assert resultado.total_registrado == 0
    assert resultado.total_ignorado == 1

    mock_inserir_historico.assert_not_called()

@patch(
    "skinexa.services.precos.service."
    "inserir_historico_preco",
)
@patch(
    "skinexa.services.precos.service."
    "obter_itens_catalogo_ids_por_nomes_mercado",
)
@patch(
    "skinexa.services.precos.service."
    "obter_plataforma_mercado_id_por_identificador",
)

def test_registrar_preco_rejeita_plataforma_indisponivel(
    mock_obter_plataforma,
    mock_obter_itens,
    mock_inserir_historico,
):
    """Testa erro quando a plataforma não está disponível."""

    conexao = Mock()

    mock_obter_plataforma.return_value = None

    with pytest.raises(
        PlataformaMercadoIndisponivel,
        match="skinport",
    ):
        registrar_precos(
            conexao,
            [_criar_preco()],
        )

    mock_obter_itens.return_value = {
        "AK-47 | Redline (Field-Tested)": 15,
    }
    mock_inserir_historico.assert_not_called()

@patch(
    "skinexa.services.precos.service."
    "inserir_historico_preco",
)
@patch(
    "skinexa.services.precos.service."
    "obter_itens_catalogo_ids_por_nomes_mercado",
)
@patch(
    "skinexa.services.precos.service."
    "obter_plataforma_mercado_id_por_identificador",
)

def test_registrar_multiplos_precos(
    mock_obter_plataforma,
    mock_obter_itens,
    mock_inserir_historico,
):
    """Testa o registro de múltiplos preços."""

    conexao = Mock()

    mock_obter_plataforma.return_value = 2

    mock_obter_itens.return_value = {
        "AK-47 | Redline (Field-Tested)": 15,
        "AWP | Asiimov (Field-Tested)": 20,
    }

    precos = [
        _criar_preco(
            nome_mercado=(
                "AK-47 | Redline (Field-Tested)"
            ),
        ),
        _criar_preco(
            nome_mercado=(
                "AWP | Asiimov (Field-Tested)"
            ),
        ),
    ]

    resultado = registrar_precos(
        conexao,
        precos,
    )

    assert resultado.total_recebido == 2
    assert resultado.total_registrado == 2
    assert resultado.total_ignorado == 0

    assert mock_inserir_historico.call_count == 2

@patch(
    "skinexa.services.precos.service."
    "inserir_historico_preco",
)
@patch(
    "skinexa.services.precos.service."
    "obter_itens_catalogo_ids_por_nomes_mercado",
)
@patch(
    "skinexa.services.precos.service."
    "obter_plataforma_mercado_id_por_identificador",
)

def test_registrar_precos_resolve_plataforma_uma_vez(
    mock_obter_plataforma,
    mock_obter_itens,
    mock_inserir_historico,
):
    """Testa o cache interno do ID da plataforma."""

    conexao = Mock()

    mock_obter_plataforma.return_value = 2

    mock_obter_itens.return_value = {
        "Item 1": 15,
        "Item 2": 20,
        "Item 3": 30,
    }

    precos = [
        _criar_preco(
            nome_mercado="Item 1",
        ),
        _criar_preco(
            nome_mercado="Item 2",
        ),
        _criar_preco(
            nome_mercado="Item 3",
        ),
    ]

    registrar_precos(
        conexao,
        precos,
    )

    mock_obter_plataforma.assert_called_once_with(
        conexao,
        "skinport",
    )

    mock_obter_itens.assert_called_once_with(
        conexao,
        {
            "Item 1",
            "Item 2",
            "Item 3",
        },
    )
    assert mock_inserir_historico.call_count == 3
    
@patch(
    "skinexa.services.precos.service."
    "inserir_historico_preco",
)
@patch(
    "skinexa.services.precos.service."
    "obter_itens_catalogo_ids_por_nomes_mercado",
)
@patch(
    "skinexa.services.precos.service."
    "obter_plataforma_mercado_id_por_identificador",
)

def test_registrar_precos_lista_vazia(
    mock_obter_plataforma,
    mock_obter_itens,
    mock_inserir_historico,
):
    """Testa registro sem preços recebidos."""

    conexao = Mock()

    resultado = registrar_precos(
        conexao,
        [],
    )

    assert resultado.total_recebido == 0
    assert resultado.total_registrado == 0
    assert resultado.total_ignorado == 0

    mock_obter_itens.assert_not_called()
    mock_obter_plataforma.assert_not_called()
    mock_inserir_historico.assert_not_called()