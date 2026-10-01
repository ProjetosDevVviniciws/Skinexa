"""Queries relacionadas ao catálogo de itens do Skinexa."""

from typing import Any

from sqlalchemy import bindparam, text
from sqlalchemy.engine import Connection

def obter_item_catalogo_por_id(
    conexao: Connection,
    item_catalogo_id: int,
) -> dict[str, Any] | None:
    """Obtém um item do catálogo pelo identificador interno."""

    if item_catalogo_id <= 0:
        return None

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

    resultado = (
        conexao.execute(
            consulta,
            {
                "item_catalogo_id": item_catalogo_id,
            },
        )
        .mappings()
        .first()
    )

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

    nome_normalizado = nome_mercado.strip()

    if app_id <= 0 or not nome_normalizado:
        return None

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

    resultado = (
        conexao.execute(
            consulta,
            {
                "app_id": app_id,
                "nome_mercado": nome_normalizado,
            },
        )
        .mappings()
        .first()
    )

    if resultado is None:
        return None

    return dict(resultado)

def obter_itens_catalogo_ids_por_nomes_mercado(
    conexao: Connection,
    nomes_mercado: set[str],
    *,
    app_id: int = 730,
) -> dict[str, int]:
    """
    Obtém IDs dos itens do catálogo
    pelos respectivos nomes de mercado.
    """

    if not nomes_mercado:
        return {}

    consulta = text(
        """
        SELECT
            id,
            nome_mercado
        FROM itens_catalogo
        WHERE app_id = :app_id
          AND nome_mercado IN :nomes_mercado
        """
    ).bindparams(
        bindparam(
            "nomes_mercado",
            expanding=True,
        )
    )

    resultado = conexao.execute(
        consulta,
        {
            "app_id": app_id,
            "nomes_mercado": tuple(nomes_mercado),
        },
    )

    return {
        str(registro.nome_mercado): int(registro.id)
        for registro in resultado
    }

def listar_itens_catalogo(
    conexao: Connection,
    *,
    limite: int,
    deslocamento: int,
) -> list[dict[str, Any]]:
    """Lista itens do catálogo com paginação."""

    if limite < 1:
        raise ValueError(
            "O limite deve ser maior que zero."
        )

    if deslocamento < 0:
        raise ValueError(
            "O deslocamento não pode ser negativo."
        )

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