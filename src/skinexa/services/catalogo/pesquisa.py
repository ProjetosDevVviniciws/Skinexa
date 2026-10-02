"""Serviços relacionados à pesquisa de itens do catálogo."""

from sqlalchemy.engine import Connection

from skinexa.database.queries.itens_catalogo import (
    pesquisar_itens_catalogo_por_nome,
)

from skinexa.dto.catalogo.item import ItemCatalogoDTO

from skinexa.services.catalogo.service import (
    converter_item_catalogo,
    obter_item,
)

def pesquisar_itens_por_nome(
    conexao: Connection,
    *,
    termo: str,
    limite: int = 20,
    deslocamento: int = 0,
) -> list[ItemCatalogoDTO]:
    """Pesquisa itens do catálogo por nome."""

    registros = pesquisar_itens_catalogo_por_nome(
        conexao,
        termo=termo,
        limite=limite,
        deslocamento=deslocamento,
    )

    return [
        converter_item_catalogo(registro)
        for registro in registros
    ]
    
def pesquisar_item_por_identificador(
    conexao: Connection,
    identificador: int,
) -> ItemCatalogoDTO | None:
    """Pesquisa um item pelo identificador interno."""

    return obter_item(
        conexao,
        identificador,
    )
    
def pesquisar_itens_globalmente(
    conexao: Connection,
    *,
    termo: str,
    limite: int = 20,
) -> list[ItemCatalogoDTO]:
    """Pesquisa itens do catálogo por diferentes identificadores."""

    termo_normalizado = termo.strip()

    if not termo_normalizado:
        return []

    if limite < 1:
        raise ValueError(
            "O limite deve ser maior que zero."
        )

    itens: list[ItemCatalogoDTO] = []
    ids_adicionados: set[int] = set()

    if termo_normalizado.isdigit():
        identificador = int(
            termo_normalizado
        )

        if identificador > 0:
            item = pesquisar_item_por_identificador(
                conexao,
                identificador,
            )

            if item is not None:
                itens.append(item)
                ids_adicionados.add(item.id)

    itens_por_nome = pesquisar_itens_por_nome(
        conexao,
        termo=termo_normalizado,
        limite=limite,
        deslocamento=0,
    )

    for item in itens_por_nome:
        if item.id in ids_adicionados:
            continue

        itens.append(item)
        ids_adicionados.add(item.id)

        if len(itens) >= limite:
            break

    return itens       