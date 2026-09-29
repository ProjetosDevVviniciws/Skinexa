"""Queries relacionadas ao catálogo de itens do Skinexa."""

from typing import Any

from sqlalchemy import text

from skinexa.database.connection import engine

def buscar_item_catalogo_por_id(
    item_catalogo_id: int,
) -> dict[str, Any] | None:
    """Busca um item do catálogo pelo identificador interno."""

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
            metadados_origem
        FROM itens_catalogo
        WHERE id = :item_catalogo_id
        LIMIT 1
        """
    )

    with engine.connect() as conexao:
        registro = (
            conexao.execute(
                consulta,
                {
                    "item_catalogo_id": item_catalogo_id,
                },
            )
            .mappings()
            .first()
        )

    if registro is None:
        return None

    return dict(registro)

def buscar_item_catalogo_por_nome_mercado(
    *,
    app_id: int,
    nome_mercado: str,
) -> dict[str, Any] | None:
    """Busca um item pela sua identificação canônica externa."""

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
            metadados_origem
        FROM itens_catalogo
        WHERE app_id = :app_id
          AND nome_mercado = :nome_mercado
        LIMIT 1
        """
    )

    with engine.connect() as conexao:
        registro = (
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

    if registro is None:
        return None

    return dict(registro)

def listar_itens_catalogo(
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
            metadados_origem
        FROM itens_catalogo
        ORDER BY nome_exibicao ASC, id ASC
        LIMIT :limite
        OFFSET :deslocamento
        """
    )

    with engine.connect() as conexao:
        registros = (
            conexao.execute(
                consulta,
                {
                    "limite": limite,
                    "deslocamento": deslocamento,
                },
            )
            .mappings()
            .all()
        )

    return [
        dict(registro)
        for registro in registros
    ]

def contar_itens_catalogo() -> int:
    """Retorna a quantidade total de itens do catálogo."""

    consulta = text(
        """
        SELECT COUNT(*)
        FROM itens_catalogo
        """
    )

    with engine.connect() as conexao:
        total = conexao.execute(
            consulta
        ).scalar_one()

    return int(total)