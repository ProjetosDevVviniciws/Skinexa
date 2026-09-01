from datetime import datetime
from decimal import Decimal

from skinexa.domain.preco import PrecoMercado
from skinexa.dto.skinport.preco import PrecoSkinportDTO
from skinexa.integrations.skinport.normalizador_preco import (
    normalizar_preco_skinport,
)

def test_normalizar_preco_skinport():
    """Testa a normalização de um preço da Skinport."""

    atualizado_em = datetime(
        2026,
        9,
        1,
        12,
        30,
    )

    preco_skinport = PrecoSkinportDTO(
        market_hash_name=(
            "AK-47 | Redline (Field-Tested)"
        ),
        currency="BRL",
        min_price=Decimal("145.50"),
        max_price=Decimal("230.00"),
        mean_price=Decimal("167.30"),
        median_price=Decimal("160.00"),
        quantity=42,
        updated_at=atualizado_em,
    )

    resultado = normalizar_preco_skinport(
        preco_skinport
    )

    assert resultado == PrecoMercado(
        nome_mercado=(
            "AK-47 | Redline (Field-Tested)"
        ),
        plataforma="skinport",
        moeda="BRL",
        menor_preco=Decimal("145.50"),
        maior_preco=Decimal("230.00"),
        preco_medio=Decimal("167.30"),
        preco_mediano=Decimal("160.00"),
        maior_ordem_compra=None,
        quantidade_anuncios=42,
        volume_vendas=None,
        atualizado_na_origem_em=atualizado_em,
    )
    
def test_normalizar_preco_skinport_com_valores_ausentes():
    """Testa a normalização quando preços opcionais estão ausentes."""

    preco_skinport = PrecoSkinportDTO(
        market_hash_name="AK-47 | Redline",
        currency="BRL",
        min_price=None,
        max_price=None,
        mean_price=None,
        median_price=None,
        quantity=None,
        updated_at=None,
    )

    resultado = normalizar_preco_skinport(
        preco_skinport
    )

    assert resultado.menor_preco is None
    assert resultado.maior_preco is None
    assert resultado.preco_medio is None
    assert resultado.preco_mediano is None
    assert resultado.maior_ordem_compra is None
    assert resultado.quantidade_anuncios is None
    assert resultado.volume_vendas is None
    assert resultado.atualizado_na_origem_em is None