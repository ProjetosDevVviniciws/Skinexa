from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Connection

def obter_item_catalogo_por_id(
    conexao: Connection,
    item_catalogo_id: int,
) -> dict[str, Any] | None:
    """Obtém um item do catálogo pelo identificador interno."""

    consulta = text(
        """
        SELECT
            id,
            app_id,
            nome_mercado,
            nome_exibicao,
            tipo_item,
            nome_arma,
            nome_acabamento,
            estado_exterior,
            raridade,
            qualidade,
            colecao,
            descricao,
            indice_pintura,
            float_minimo,
            float_maximo,
            variante_stattrak,
            variante_souvenir,
            comercializavel,
            mercadoria_generica,
            steam_class_id,
            steam_instance_id,
            url_icone,
            url_icone_grande,
            tags,
            metadados_origem,
            criado_em,
            atualizado_em
        FROM itens_catalogo
        WHERE id = :item_catalogo_id
        LIMIT 1
        """
    )

    resultado = conexao.execute(
        consulta,
        {
            "item_catalogo_id": item_catalogo_id,
        },
    ).mappings().first()

    if resultado is None:
        return None

    return dict(resultado)

def obter_item_catalogo_por_nome_mercado(
    conexao: Connection,
    *,
    app_id: int,
    nome_mercado: str,
) -> dict[str, Any] | None:
    """
    Obtém um item do catálogo pelo app_id
    e nome de mercado.
    """

    consulta = text(
        """
        SELECT
            id,
            app_id,
            nome_mercado,
            nome_exibicao,
            tipo_item,
            nome_arma,
            nome_acabamento,
            estado_exterior,
            raridade,
            qualidade,
            colecao,
            descricao,
            indice_pintura,
            float_minimo,
            float_maximo,
            variante_stattrak,
            variante_souvenir,
            comercializavel,
            mercadoria_generica,
            steam_class_id,
            steam_instance_id,
            url_icone,
            url_icone_grande,
            tags,
            metadados_origem,
            criado_em,
            atualizado_em
        FROM itens_catalogo
        WHERE app_id = :app_id
          AND nome_mercado = :nome_mercado
        LIMIT 1
        """
    )

    resultado = conexao.execute(
        consulta,
        {
            "app_id": app_id,
            "nome_mercado": nome_mercado,
        },
    ).mappings().first()

    if resultado is None:
        return None

    return dict(resultado)

def listar_itens_catalogo(
    conexao: Connection,
    *,
    limite: int,
    deslocamento: int,
) -> list[dict[str, Any]]:
    """Lista itens do catálogo com paginação."""

    consulta = text(
        """
        SELECT
            id,
            app_id,
            nome_mercado,
            nome_exibicao,
            tipo_item,
            nome_arma,
            nome_acabamento,
            estado_exterior,
            raridade,
            qualidade,
            colecao,
            descricao,
            indice_pintura,
            float_minimo,
            float_maximo,
            variante_stattrak,
            variante_souvenir,
            comercializavel,
            mercadoria_generica,
            steam_class_id,
            steam_instance_id,
            url_icone,
            url_icone_grande,
            tags,
            metadados_origem,
            criado_em,
            atualizado_em
        FROM itens_catalogo
        ORDER BY
            nome_exibicao ASC,
            id ASC
        LIMIT :limite
        OFFSET :deslocamento
        """
    )

    resultado = conexao.execute(
        consulta,
        {
            "limite": limite,
            "deslocamento": deslocamento,
        },
    )

    return [
        dict(registro._mapping)
        for registro in resultado
    ]

def contar_itens_catalogo(
    conexao: Connection,
) -> int:
    """Retorna a quantidade total de itens do catálogo."""

    consulta = text(
        """
        SELECT COUNT(*)
        FROM itens_catalogo
        """
    )

    resultado = conexao.execute(
        consulta
    ).scalar_one()

    return int(resultado)