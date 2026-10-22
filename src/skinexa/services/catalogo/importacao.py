from sqlalchemy import text
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

def verificar_item_catalogo_importacao(
    conexao: Connection,
    *,
    app_id: int,
    nome_mercado: str,
    tipo_item: str,
) -> None:
    """Verifica se o tipo de um item existente é compatível."""

    consulta = text(
        """
        SELECT
            id,
            tipo_item
        FROM itens_catalogo
        WHERE app_id = :app_id
          AND nome_mercado = :nome_mercado
        LIMIT 1
        FOR UPDATE
        """
    )

    registro = (
        conexao.execute(
            consulta,
            {
                "app_id": app_id,
                "nome_mercado": nome_mercado,
            },
        )
        .mappings()
        .first()
    )

    if registro is None:
        return

    if registro["tipo_item"] != tipo_item:
        raise RuntimeError(
            "Conflito de tipo para o item comercial "
            f"{nome_mercado}: "
            f"existente={registro['tipo_item']}, "
            f"recebido={tipo_item}."
        )

def verificar_variante_catalogo_importacao(
    conexao: Connection,
    *,
    fonte: str,
    id_externo: str,
    item_catalogo_id: int,
) -> None:
    """Verifica se uma variante pertence ao item esperado."""

    consulta = text(
        """
        SELECT
            id,
            item_catalogo_id
        FROM variantes_itens_catalogo
        WHERE fonte = :fonte
          AND id_externo = :id_externo
        LIMIT 1
        FOR UPDATE
        """
    )

    registro = (
        conexao.execute(
            consulta,
            {
                "fonte": fonte,
                "id_externo": id_externo,
            },
        )
        .mappings()
        .first()
    )

    if registro is None:
        return

    if int(registro["item_catalogo_id"]) != item_catalogo_id:
        raise RuntimeError(
            "Conflito de vínculo para a variante "
            f"{fonte}:{id_externo}. "
            f"Item esperado: {item_catalogo_id}. "
            f"Item existente: {registro['item_catalogo_id']}."
        )

def importar_lote_catalogo(
    conexao: Connection,
    relatorio: RelatorioNormalizacaoCatalogoDTO,
    *,
    validar_vinculos: bool = False,
) -> tuple[int, int]:
    """
    Persiste itens comerciais e variantes de um lote normalizado.

    Quando validar_vinculos=True, impede alterações indevidas
    de tipos comerciais e de associações externas.

    A conexão e a transação são controladas pelo chamador.
    """

    total_itens = 0
    total_variantes = 0

    for item in relatorio.itens:
        if validar_vinculos:
            verificar_item_catalogo_importacao(
                conexao,
                app_id=item.app_id,
                nome_mercado=item.nome_mercado,
                tipo_item=item.tipo_item,
            )

        inserir_ou_atualizar_item_catalogo_importacao(
            conexao,
            item,
        )

        if validar_vinculos:
            verificar_item_catalogo_importacao(
                conexao,
                app_id=item.app_id,
                nome_mercado=item.nome_mercado,
                tipo_item=item.tipo_item,
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

        item_catalogo_id = int(
            item_comercial["id"]
        )

        if validar_vinculos:
            verificar_variante_catalogo_importacao(
                conexao,
                fonte=variante.fonte,
                id_externo=variante.id_externo,
                item_catalogo_id=item_catalogo_id,
            )

        if validar_vinculos:
            inserir_ou_atualizar_variante_catalogo_importacao(
                conexao,
                item_catalogo_id=item_catalogo_id,
                variante=variante,
                proteger_vinculo=True,
            )

            verificar_variante_catalogo_importacao(
                conexao,
                fonte=variante.fonte,
                id_externo=variante.id_externo,
                item_catalogo_id=item_catalogo_id,
            )

        else:
            inserir_ou_atualizar_variante_catalogo_importacao(
                conexao,
                item_catalogo_id=item_catalogo_id,
                variante=variante,
            )

        total_variantes += 1

    return total_itens, total_variantes