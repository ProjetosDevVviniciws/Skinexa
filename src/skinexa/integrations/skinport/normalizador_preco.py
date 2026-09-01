from skinexa.domain.preco import PrecoMercado
from skinexa.dto.skinport.preco import PrecoSkinportDTO

def normalizar_preco_skinport(
    preco: PrecoSkinportDTO,
) -> PrecoMercado:
    """
    Converte os dados de preço da Skinport
    para o formato interno do Skinexa.
    """

    return PrecoMercado(
        nome_mercado=preco.market_hash_name,
        plataforma="skinport",
        moeda=preco.currency,
        menor_preco=preco.min_price,
        maior_preco=preco.max_price,
        preco_medio=preco.mean_price,
        preco_mediano=preco.median_price,
        maior_ordem_compra=None,
        quantidade_anuncios=preco.quantity,
        volume_vendas=None,
        atualizado_na_origem_em=preco.updated_at,
    )