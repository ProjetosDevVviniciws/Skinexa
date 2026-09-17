from datetime import datetime

from decimal import Decimal

from unittest.mock import Mock, patch

from skinexa.domain.comparacao_preco import (
    PrecoComparacao,
)
from skinexa.services.precos.comparacao import (
    obter_comparacao_precos,
)

@patch(
    "skinexa.services.precos.comparacao."
    "obter_ultimos_precos_item_por_plataforma",
)

def test_obter_comparacao_precos(
    mock_obter_precos,
):
    """Testa obtenção dos preços para comparação."""

    conexao = Mock()

    coletado_em = datetime(
        2026,
        9,
        16,
        14,
        0,
    )

    atualizado_em = datetime(
        2026,
        9,
        16,
        13,
        55,
    )

    mock_obter_precos.return_value = [
        {
            "plataforma": "skinport",
            "moeda": "BRL",
            "menor_preco": Decimal("103.16"),
            "maior_preco": Decimal("150.00"),
            "preco_medio": Decimal("120.00"),
            "preco_mediano": Decimal("115.00"),
            "maior_ordem_compra": None,
            "quantidade_anuncios": 134,
            "volume_vendas": None,
            "coletado_em": coletado_em,
            "atualizado_na_origem_em": atualizado_em,
        },
        {
            "plataforma": "csfloat",
            "moeda": "BRL",
            "menor_preco": Decimal("98.40"),
            "maior_preco": Decimal("140.00"),
            "preco_medio": Decimal("110.00"),
            "preco_mediano": Decimal("105.00"),
            "maior_ordem_compra": None,
            "quantidade_anuncios": 42,
            "volume_vendas": None,
            "coletado_em": coletado_em,
            "atualizado_na_origem_em": atualizado_em,
        },
    ]

    resultado = obter_comparacao_precos(
        conexao,
        item_catalogo_id=1,
    )

    assert resultado == (
        PrecoComparacao(
            plataforma="skinport",
            moeda="BRL",
            menor_preco=Decimal("103.16"),
            maior_preco=Decimal("150.00"),
            preco_medio=Decimal("120.00"),
            preco_mediano=Decimal("115.00"),
            maior_ordem_compra=None,
            quantidade_anuncios=134,
            volume_vendas=None,
            coletado_em=coletado_em,
            atualizado_na_origem_em=atualizado_em,
        ),
        PrecoComparacao(
            plataforma="csfloat",
            moeda="BRL",
            menor_preco=Decimal("98.40"),
            maior_preco=Decimal("140.00"),
            preco_medio=Decimal("110.00"),
            preco_mediano=Decimal("105.00"),
            maior_ordem_compra=None,
            quantidade_anuncios=42,
            volume_vendas=None,
            coletado_em=coletado_em,
            atualizado_na_origem_em=atualizado_em,
        ),
    )

    mock_obter_precos.assert_called_once_with(
        conexao,
        item_catalogo_id=1,
    )
    
@patch(
    "skinexa.services.precos.comparacao."
    "obter_ultimos_precos_item_por_plataforma",
)

def test_obter_comparacao_precos_sem_historico(
    mock_obter_precos,
):
    """Testa comparação quando não existem preços."""

    conexao = Mock()

    mock_obter_precos.return_value = []

    resultado = obter_comparacao_precos(
        conexao,
        item_catalogo_id=999,
    )

    assert resultado == ()

    mock_obter_precos.assert_called_once_with(
        conexao,
        item_catalogo_id=999,
    )