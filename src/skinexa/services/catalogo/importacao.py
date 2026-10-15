from sqlalchemy.engine import Connection

from skinexa.database.queries.itens_catalogo import (
    inserir_ou_atualizar_item_catalogo_importacao,
    obter_item_catalogo_por_nome_mercado,
)

from skinexa.database.queries.variantes_itens_catalogo import (
    inserir_ou_atualizar_variante_catalogo_importacao,
)

from skinexa.dto.catalogo.normalizacao_lote import (
    RelatorioNormalizacaoCatalogoDTO,
)

def importar_lote_catalogo(
    conexao: Connection,
    relatorio: RelatorioNormalizacaoCatalogoDTO,
) -> tuple[int, int]:
    """
    Persiste itens comerciais e variantes de um lote normalizado.

    A conexão e a transação são controladas pelo chamador.
    """

    total_itens = 0
    total_variantes = 0

    for item in relatorio.itens:
        inserir_ou_atualizar_item_catalogo_importacao(
            conexao,
            item,
        )

        total_itens += 1

    for variante in relatorio.variantes:
        item_comercial = obter_item_catalogo_por_nome_mercado(
            conexao,
            app_id=variante.app_id,
            nome_mercado=variante.nome_mercado,
        )

        if item_comercial is None:
            raise RuntimeError(
                "Item comercial não encontrado para a variante: "
                f"{variante.nome_mercado}"
            )

        inserir_ou_atualizar_variante_catalogo_importacao(
            conexao,
            item_catalogo_id=item_comercial["id"],
            variante=variante,
        )

        total_variantes += 1

    return total_itens, total_variantes