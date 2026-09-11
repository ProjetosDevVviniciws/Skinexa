from decimal import Decimal
from statistics import median

from skinexa.domain.preco import PrecoMercado
from skinexa.dto.csfloat.preco import (
    PrecoCSFloatDTO,
)

from skinexa.utils.monetario import arredondar_moeda

class ErroNormalizacaoPrecoCSFloat(RuntimeError):
    """Erro ao normalizar preços recebidos da CSFloat."""

def normalizar_precos_csfloat(
    itens: tuple[PrecoCSFloatDTO, ...],
    *,
    taxa_usd_brl: Decimal,
) -> PrecoMercado:
    """
    Consolida anúncios da CSFloat e converte
    seus preços de USD para BRL.
    """

    if not itens:
        raise ErroNormalizacaoPrecoCSFloat(
            "Não existem preços da CSFloat para normalizar."
        )

    if taxa_usd_brl <= 0:
        raise ErroNormalizacaoPrecoCSFloat(
            "A taxa de conversão USD/BRL é inválida."
        )
    
    nome_mercado = itens[0].market_hash_name

    for item in itens:
        if item.market_hash_name != nome_mercado:
            raise ErroNormalizacaoPrecoCSFloat(
                "Os preços recebidos pertencem "
                "a itens de mercado diferentes."
            )

    precos_brl = [
        item.preco * taxa_usd_brl
        for item in itens
    ]

    menor_preco = arredondar_moeda(min(precos_brl)) 
    maior_preco = arredondar_moeda(max(precos_brl))

    preco_medio = arredondar_moeda(
        sum(
            precos_brl,
            Decimal("0"),
        )
        / Decimal(len(precos_brl))
    )

    preco_mediano = arredondar_moeda(median(precos_brl))

    datas = [
        item.criado_em
        for item in itens
        if item.criado_em is not None
    ]

    atualizado_na_origem_em = (
        max(datas)
        if datas
        else None
    )

    return PrecoMercado(
        nome_mercado=nome_mercado,
        plataforma="csfloat",
        moeda="BRL",
        menor_preco=menor_preco,
        maior_preco=maior_preco,
        preco_medio=preco_medio,
        preco_mediano=preco_mediano,
        maior_ordem_compra=None,
        quantidade_anuncios=len(itens),
        volume_vendas=None,
        atualizado_na_origem_em=(
            atualizado_na_origem_em
        ),
    )