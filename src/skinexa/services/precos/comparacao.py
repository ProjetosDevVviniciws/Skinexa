from sqlalchemy.engine import Connection

from skinexa.database.queries.historico_precos import (
    obter_ultimos_precos_item_por_plataforma,
)
from skinexa.domain.comparacao_preco import (
    PrecoComparacao,
)

def obter_comparacao_precos(
    conexao: Connection,
    *,
    item_catalogo_id: int,
) -> tuple[PrecoComparacao, ...]:
    """
    Obtém os preços mais recentes de um item
    disponíveis em cada marketplace.
    """

    registros = (
        obter_ultimos_precos_item_por_plataforma(
            conexao,
            item_catalogo_id=item_catalogo_id,
        )
    )

    return tuple(
        _criar_preco_comparacao(registro)
        for registro in registros
    )

def _criar_preco_comparacao(
    registro: dict,
) -> PrecoComparacao:
    """Converte um registro do banco para o domínio."""

    return PrecoComparacao(
        plataforma=registro["plataforma"],
        moeda=registro["moeda"],
        menor_preco=registro["menor_preco"],
        maior_preco=registro["maior_preco"],
        preco_medio=registro["preco_medio"],
        preco_mediano=registro["preco_mediano"],
        maior_ordem_compra=registro[
            "maior_ordem_compra"
        ],
        quantidade_anuncios=registro[
            "quantidade_anuncios"
        ],
        volume_vendas=registro["volume_vendas"],
        coletado_em=registro["coletado_em"],
        atualizado_na_origem_em=registro[
            "atualizado_na_origem_em"
        ],
    )