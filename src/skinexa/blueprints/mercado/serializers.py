from flask import url_for

from skinexa.dto.catalogo.item import (
    ItemCatalogoDTO,
)

from skinexa.dto.catalogo.paginacao import (
    PaginaItensCatalogoDTO,
)

from skinexa.utils.raridades import (
    obter_cor_raridade,
)

from typing import Any

from skinexa.domain.comparacao_preco import (
    PrecoComparacao,
)

from skinexa.utils.serializadores import (
    serializar_datetime,
    serializar_decimal,
)

from skinexa.dto.catalogo.autocomplete import (
    SugestaoItemCatalogoDTO,
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

def serializar_item_mercado(
    item: ItemCatalogoDTO,
) -> dict[str, Any]:
    """Serializa um item para os cards da página Mercado."""

    return {
        "id": item.id,
        "nome_exibicao": item.nome_exibicao,
        "tipo_item": item.tipo_item,
        "nome_arma": item.nome_arma,
        "nome_acabamento": item.nome_acabamento,
        "estado_exterior": item.estado_exterior,
        "raridade": item.raridade,
        "cor_raridade": obter_cor_raridade(
            item.raridade
        ),
        "url_icone": item.url_icone,
        "url_icone_grande": item.url_icone_grande,
        "variante_stattrak": item.variante_stattrak,
        "variante_souvenir": item.variante_souvenir,
        "url_detalhes": url_for(
            "mercado.item",
            item_catalogo_id=item.id,
        ),
    }

def serializar_pagina_mercado(
    resultado: PaginaItensCatalogoDTO,
    *,
    ordenacao: str,
) -> dict[str, Any]:
    """Serializa itens e informações de paginação do Mercado."""

    return {
        "itens": [
            serializar_item_mercado(item)
            for item in resultado.itens
        ],
        "paginacao": {
            "pagina": resultado.pagina,
            "por_pagina": resultado.por_pagina,
            "total_itens": resultado.total_itens,
            "total_paginas": resultado.total_paginas,
            "tem_anterior": resultado.tem_anterior,
            "tem_proxima": resultado.tem_proxima,
        },
        "ordenacao": ordenacao,
    } 

def serializar_sugestao_mercado(
    sugestao: SugestaoItemCatalogoDTO,
) -> dict[str, Any]:
    """Serializa uma sugestão de item para o autocomplete."""

    return {
        "id": sugestao.id,
        "nome_mercado": sugestao.nome_mercado,
        "nome_exibicao": sugestao.nome_exibicao,
        "tipo_item": sugestao.tipo_item,
        "url_icone": sugestao.url_icone,
        "url_detalhes": url_for(
            "mercado.item",
            item_catalogo_id=sugestao.id,
        ),
    }