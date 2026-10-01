"""Orquestra as queries sem assumir responsabilidade sobre a conexão com o banco de dados."""

from typing import Any

from sqlalchemy.engine import Connection

from skinexa.database.queries.itens_catalogo import (
    contar_itens_catalogo,
    listar_itens_catalogo,
    obter_item_catalogo_por_id,
    obter_item_catalogo_por_nome_mercado,
)

from skinexa.dto.catalogo.item import ItemCatalogoDTO

def _converter_item_catalogo(
    registro: dict[str, Any],
) -> ItemCatalogoDTO:
    """Converte um registro do banco em DTO de catálogo."""

    return ItemCatalogoDTO(
        id=int(registro["id"]),
        app_id=int(registro["app_id"]),
        nome_mercado=str(registro["nome_mercado"]),
        nome_exibicao=str(registro["nome_exibicao"]),
        tipo_item=str(registro["tipo_item"]),
        nome_arma=registro["nome_arma"],
        nome_acabamento=registro["nome_acabamento"],
        estado_exterior=registro["estado_exterior"],
        raridade=registro["raridade"],
        qualidade=registro["qualidade"],
        colecao=registro["colecao"],
        descricao=registro["descricao"],
        indice_pintura=registro["indice_pintura"],
        float_minimo=registro["float_minimo"],
        float_maximo=registro["float_maximo"],
        variante_stattrak=bool(
            registro["variante_stattrak"]
        ),
        variante_souvenir=bool(
            registro["variante_souvenir"]
        ),
        comercializavel=bool(
            registro["comercializavel"]
        ),
        mercadoria_generica=bool(
            registro["mercadoria_generica"]
        ),
        steam_class_id=registro["steam_class_id"],
        steam_instance_id=registro["steam_instance_id"],
        url_icone=registro["url_icone"],
        url_icone_grande=registro["url_icone_grande"],
        tags=registro["tags"],
        metadados_origem=registro["metadados_origem"],
    )

def obter_item(
    conexao: Connection,
    item_catalogo_id: int,
) -> ItemCatalogoDTO | None:
    """Obtém um item do catálogo pelo identificador interno."""

    registro = obter_item_catalogo_por_id(
        conexao,
        item_catalogo_id,
    )

    if registro is None:
        return None

    return _converter_item_catalogo(
        registro
    )

def obter_item_por_nome_mercado(
    conexao: Connection,
    *,
    app_id: int,
    nome_mercado: str,
) -> ItemCatalogoDTO | None:
    """Obtém um item pelo app_id e nome de mercado."""

    registro = obter_item_catalogo_por_nome_mercado(
        conexao,
        app_id=app_id,
        nome_mercado=nome_mercado,
    )

    if registro is None:
        return None

    return _converter_item_catalogo(
        registro
    )
    
def listar_itens(
    conexao: Connection,
    *,
    limite: int,
    deslocamento: int,
) -> list[ItemCatalogoDTO]:
    """Lista itens do catálogo com paginação."""

    registros = listar_itens_catalogo(
        conexao,
        limite=limite,
        deslocamento=deslocamento,
    )

    return [
        _converter_item_catalogo(registro)
        for registro in registros
    ]

def contar_itens(
    conexao: Connection,
) -> int:
    """Retorna a quantidade total de itens do catálogo."""

    return contar_itens_catalogo(
        conexao
    )