from typing import Any

from skinexa.domain.comparacao_preco import (
    PrecoComparacao,
)

from skinexa.utils.serializadores import (
    serializar_datetime,
    serializar_decimal,
)

def serializar_preco_comparacao(
    preco: PrecoComparacao,
) -> dict[str, Any]:
    """Serializa um preço de comparação para resposta HTTP."""

    return {
        "plataforma": preco.plataforma,
        "moeda": preco.moeda,
        "menor_preco": serializar_decimal(
            preco.menor_preco
        ),
        "maior_preco": serializar_decimal(
            preco.maior_preco
        ),
        "preco_medio": serializar_decimal(
            preco.preco_medio
        ),
        "preco_mediano": serializar_decimal(
            preco.preco_mediano
        ),
        "maior_ordem_compra": serializar_decimal(
            preco.maior_ordem_compra
        ),
        "quantidade_anuncios": preco.quantidade_anuncios,
        "volume_vendas": preco.volume_vendas,
        "coletado_em": serializar_datetime(
            preco.coletado_em
        ),
        "atualizado_na_origem_em": serializar_datetime(
            preco.atualizado_na_origem_em
        ),
    }