from skinexa.database.connection import engine

from skinexa.domain.comparacao_preco import PrecoComparacao
from skinexa.domain.preco import UltimoPrecoMercado

from skinexa.services.precos.service import (
    obter_ultimos_precos,
)

from skinexa.services.precos.comparacao import obter_comparacao_precos

def consultar_ultimos_precos(
    *,
    item_catalogo_ids: set[int],
    plataforma: str,
) -> dict[int, UltimoPrecoMercado]:
    """
    Consulta o último preço conhecido dos itens
    para uma determinada plataforma.
    """

    if not item_catalogo_ids:
        return {}

    with engine.connect() as conexao:
        return obter_ultimos_precos(
            conexao,
            item_catalogo_ids=item_catalogo_ids,
            plataforma=plataforma,
        )
        
def consultar_comparacao_precos(
    *,
    item_catalogo_id: int,
) -> tuple[PrecoComparacao, ...]:
    """
    Consulta os preços mais recentes de um item
    disponíveis nos marketplaces.
    """

    with engine.connect() as conexao:
        return obter_comparacao_precos(
            conexao,
            item_catalogo_id=item_catalogo_id,
        )