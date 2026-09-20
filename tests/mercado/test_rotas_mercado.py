from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

from skinexa.domain.comparacao_preco import (
    PrecoComparacao,
)

@patch(
    "skinexa.blueprints.mercado.routes."
    "consultar_comparacao_precos",
)

def test_precos_item_retorna_comparacao(
    mock_consultar_comparacao_precos,
    client,
):
    """Testa o retorno dos preços de diferentes marketplaces."""

    mock_consultar_comparacao_precos.return_value = (
        PrecoComparacao(
            plataforma="skinport",
            moeda="BRL",
            menor_preco=Decimal("103.16"),
            maior_preco=Decimal("150.00"),
            preco_medio=Decimal("120.50"),
            preco_mediano=Decimal("118.00"),
            maior_ordem_compra=None,
            quantidade_anuncios=134,
            volume_vendas=None,
            coletado_em=datetime(
                2026,
                9,
                17,
                14,
                30,
            ),
            atualizado_na_origem_em=datetime(
                2026,
                9,
                17,
                14,
                25,
            ),
        ),
        PrecoComparacao(
            plataforma="csfloat",
            moeda="BRL",
            menor_preco=Decimal("98.40"),
            maior_preco=Decimal("145.00"),
            preco_medio=Decimal("115.00"),
            preco_mediano=Decimal("110.00"),
            maior_ordem_compra=None,
            quantidade_anuncios=42,
            volume_vendas=None,
            coletado_em=datetime(
                2026,
                9,
                17,
                14,
                31,
            ),
            atualizado_na_origem_em=None,
        ),
    )

    resposta = client.get(
        "/mercado/item/153/precos",
    )

    assert resposta.status_code == 200

    dados = resposta.get_json()

    assert dados == {
        "item_catalogo_id": 153,
        "mercados": [
            {
                "plataforma": "skinport",
                "moeda": "BRL",
                "menor_preco": "103.16",
                "maior_preco": "150.00",
                "preco_medio": "120.50",
                "preco_mediano": "118.00",
                "maior_ordem_compra": None,
                "quantidade_anuncios": 134,
                "volume_vendas": None,
                "coletado_em": (
                    "2026-09-17T14:30:00"
                ),
                "atualizado_na_origem_em": (
                    "2026-09-17T14:25:00"
                ),
            },
            {
                "plataforma": "csfloat",
                "moeda": "BRL",
                "menor_preco": "98.40",
                "maior_preco": "145.00",
                "preco_medio": "115.00",
                "preco_mediano": "110.00",
                "maior_ordem_compra": None,
                "quantidade_anuncios": 42,
                "volume_vendas": None,
                "coletado_em": (
                    "2026-09-17T14:31:00"
                ),
                "atualizado_na_origem_em": None,
            },
        ],
    }

    mock_consultar_comparacao_precos.assert_called_once_with(
        item_catalogo_id=153,
    )
    
@patch(
    "skinexa.blueprints.mercado.routes."
    "consultar_comparacao_precos",
)

def test_precos_item_sem_precos_retorna_lista_vazia(
    mock_consultar_comparacao_precos,
    client,
):
    """Testa item sem preços coletados."""

    mock_consultar_comparacao_precos.return_value = ()

    resposta = client.get(
        "/mercado/item/153/precos",
    )

    assert resposta.status_code == 200

    assert resposta.get_json() == {
        "item_catalogo_id": 153,
        "mercados": [],
    }

    mock_consultar_comparacao_precos.assert_called_once_with(
        item_catalogo_id=153,
    )