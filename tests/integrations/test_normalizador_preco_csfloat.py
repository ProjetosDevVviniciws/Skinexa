from datetime import datetime
from decimal import Decimal

import pytest

from skinexa.dto.csfloat.preco import (
    PrecoCSFloatDTO,
)
from skinexa.integrations.csfloat.normalizador_preco import (
    ErroNormalizacaoPrecoCSFloat,
    normalizar_precos_csfloat,
)

def _criar_preco_csfloat(
    *,
    nome_mercado: str = (
        "M4A1-S | Nitro (Factory New)"
    ),
    preco: Decimal = Decimal("10.00"),
    criado_em: datetime | None = datetime(
        2026,
        9,
        7,
        20,
        45,
        13,
    ),
) -> PrecoCSFloatDTO:
    """Cria um preço da CSFloat para uso nos testes."""

    return PrecoCSFloatDTO(
        market_hash_name=nome_mercado,
        preco=preco,
        criado_em=criado_em,
    )

def test_normalizar_precos_csfloat_com_sucesso():
    """Testa a consolidação de vários preços da CSFloat."""

    itens = (
        _criar_preco_csfloat(
            preco=Decimal("10.00"),
        ),
        _criar_preco_csfloat(
            preco=Decimal("20.00"),
        ),
        _criar_preco_csfloat(
            preco=Decimal("30.00"),
        ),
    )

    resultado = normalizar_precos_csfloat(
        itens,
        taxa_usd_brl=Decimal("5.00"),
    )

    assert resultado.nome_mercado == (
        "M4A1-S | Nitro (Factory New)"
    )
    assert resultado.plataforma == "csfloat"
    assert resultado.moeda == "BRL"

    assert resultado.menor_preco == Decimal("50.00")
    assert resultado.maior_preco == Decimal("150.00")
    assert resultado.preco_medio == Decimal("100.00")
    assert resultado.preco_mediano == Decimal("100.00")

    assert resultado.maior_ordem_compra is None
    assert resultado.quantidade_anuncios == 3
    assert resultado.volume_vendas is None

def test_normalizar_precos_csfloat_com_um_item():
    """Testa a normalização de apenas um preço."""

    itens = (
        _criar_preco_csfloat(
            preco=Decimal("15.50"),
        ),
    )

    resultado = normalizar_precos_csfloat(
        itens,
        taxa_usd_brl=Decimal("5.00"),
    )

    assert resultado.menor_preco == Decimal("77.50")
    assert resultado.maior_preco == Decimal("77.50")
    assert resultado.preco_medio == Decimal("77.50")
    assert resultado.preco_mediano == Decimal("77.50")
    assert resultado.quantidade_anuncios == 1

def test_normalizar_precos_csfloat_mediana_par():
    """Testa a mediana com quantidade par de preços."""

    itens = (
        _criar_preco_csfloat(
            preco=Decimal("10.00"),
        ),
        _criar_preco_csfloat(
            preco=Decimal("20.00"),
        ),
        _criar_preco_csfloat(
            preco=Decimal("30.00"),
        ),
        _criar_preco_csfloat(
            preco=Decimal("40.00"),
        ),
    )

    resultado = normalizar_precos_csfloat(
        itens,
        taxa_usd_brl=Decimal("5.00"),
    )

    assert resultado.preco_mediano == Decimal("125.00")

def test_normalizar_precos_csfloat_arredonda_valores():
    """Testa o arredondamento dos valores convertidos."""

    itens = (
        _criar_preco_csfloat(
            preco=Decimal("10.00"),
        ),
        _criar_preco_csfloat(
            preco=Decimal("10.01"),
        ),
    )

    resultado = normalizar_precos_csfloat(
        itens,
        taxa_usd_brl=Decimal("5.123"),
    )

    assert resultado.menor_preco == Decimal("51.23")
    assert resultado.maior_preco == Decimal("51.28")
    assert resultado.preco_medio == Decimal("51.26")
    assert resultado.preco_mediano == Decimal("51.26")

def test_normalizar_precos_csfloat_usa_data_mais_recente():
    """Testa se a data mais recente é preservada."""

    itens = (
        _criar_preco_csfloat(
            criado_em=datetime(
                2026,
                9,
                7,
                18,
                0,
            ),
        ),
        _criar_preco_csfloat(
            criado_em=datetime(
                2026,
                9,
                7,
                21,
                30,
            ),
        ),
    )

    resultado = normalizar_precos_csfloat(
        itens,
        taxa_usd_brl=Decimal("5.00"),
    )

    assert resultado.atualizado_na_origem_em == datetime(
        2026,
        9,
        7,
        21,
        30,
    )

def test_normalizar_precos_csfloat_sem_datas():
    """Testa a normalização quando as datas estão ausentes."""

    itens = (
        _criar_preco_csfloat(
            criado_em=None,
        ),
        _criar_preco_csfloat(
            criado_em=None,
        ),
    )

    resultado = normalizar_precos_csfloat(
        itens,
        taxa_usd_brl=Decimal("5.00"),
    )

    assert resultado.atualizado_na_origem_em is None

def test_normalizar_precos_csfloat_rejeita_lista_vazia():
    """Testa rejeição de conjunto vazio."""

    with pytest.raises(
        ErroNormalizacaoPrecoCSFloat,
        match="Não existem preços",
    ):
        normalizar_precos_csfloat(
            (),
            taxa_usd_brl=Decimal("5.00"),
        )

def test_normalizar_precos_csfloat_rejeita_taxa_zero():
    """Testa rejeição de taxa de câmbio igual a zero."""

    itens = (
        _criar_preco_csfloat(),
    )

    with pytest.raises(
        ErroNormalizacaoPrecoCSFloat,
        match="taxa de conversão",
    ):
        normalizar_precos_csfloat(
            itens,
            taxa_usd_brl=Decimal("0"),
        )

def test_normalizar_precos_csfloat_rejeita_taxa_negativa():
    """Testa rejeição de taxa de câmbio negativa."""

    itens = (
        _criar_preco_csfloat(),
    )

    with pytest.raises(
        ErroNormalizacaoPrecoCSFloat,
        match="taxa de conversão",
    ):
        normalizar_precos_csfloat(
            itens,
            taxa_usd_brl=Decimal("-1"),
        )

def test_normalizar_precos_csfloat_rejeita_itens_diferentes():
    """Testa rejeição de preços de skins diferentes."""

    itens = (
        _criar_preco_csfloat(
            nome_mercado="AK-47 | Redline",
        ),
        _criar_preco_csfloat(
            nome_mercado="AWP | Asiimov",
        ),
    )

    with pytest.raises(
        ErroNormalizacaoPrecoCSFloat,
        match="itens de mercado diferentes",
    ):
        normalizar_precos_csfloat(
            itens,
            taxa_usd_brl=Decimal("5.00"),
        )