"""Serviços relacionados à pesquisa de itens do catálogo."""

from sqlalchemy.engine import Connection

from skinexa.database.queries.itens_catalogo import (
    buscar_sugestoes_itens_catalogo,
    contar_itens_catalogo,
    filtrar_itens_catalogo,
    listar_itens_catalogo,
    pesquisar_itens_catalogo_por_nome,
)

from skinexa.dto.catalogo.autocomplete import (
    SugestaoItemCatalogoDTO,
)

from skinexa.dto.catalogo.item import (
    ItemCatalogoDTO
)

from skinexa.dto.catalogo.paginacao import (
    PaginaItensCatalogoDTO,
)

from skinexa.services.catalogo.service import (
    converter_item_catalogo,
    obter_item,
)

LIMITE_MAXIMO_ITENS_POR_PAGINA = 100

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

def autocomplete_itens(
    conexao: Connection,
    *,
    termo: str,
    limite: int = 10,
) -> list[SugestaoItemCatalogoDTO]:
    """Obtém sugestões de itens para autocomplete."""

    registros = buscar_sugestoes_itens_catalogo(
        conexao,
        termo=termo,
        limite=limite,
    )

    return [
        SugestaoItemCatalogoDTO(
            id=int(registro["id"]),
            nome_mercado=str(
                registro["nome_mercado"]
            ),
            nome_exibicao=str(
                registro["nome_exibicao"]
            ),
            tipo_item=str(
                registro["tipo_item"]
            ),
            url_icone=registro["url_icone"],
        )
        for registro in registros
    ]
    
def filtrar_itens(
    conexao: Connection,
    *,
    tipo_item: str | None = None,
    nome_arma: str | None = None,
    nome_acabamento: str | None = None,
    estado_exterior: str | None = None,
    raridade: str | None = None,
    colecao: str | None = None,
    variante_stattrak: bool | None = None,
    variante_souvenir: bool | None = None,
    limite: int = 20,
    deslocamento: int = 0,
    ordenacao: str = "nome_asc",
) -> list[ItemCatalogoDTO]:
    """Filtra itens do catálogo por características."""

    registros = filtrar_itens_catalogo(
        conexao,
        tipo_item=tipo_item,
        nome_arma=nome_arma,
        nome_acabamento=nome_acabamento,
        estado_exterior=estado_exterior,
        raridade=raridade,
        colecao=colecao,
        variante_stattrak=variante_stattrak,
        variante_souvenir=variante_souvenir,
        limite=limite,
        deslocamento=deslocamento,
        ordenacao=ordenacao,
    )

    return [
        converter_item_catalogo(registro)
        for registro in registros
    ]
    
def listar_itens_paginados(
    conexao: Connection,
    *,
    pagina: int = 1,
    por_pagina: int = 20,
    ordenacao: str = "nome_asc",
) -> PaginaItensCatalogoDTO:
    """Lista itens do catálogo utilizando paginação."""

    if pagina < 1:
        raise ValueError(
            "A página deve ser maior que zero."
        )

    if por_pagina < 1:
        raise ValueError(
            "A quantidade por página deve ser maior que zero."
        )

    if por_pagina > LIMITE_MAXIMO_ITENS_POR_PAGINA:
        raise ValueError(
            "A quantidade por página não pode ser maior que 100."
        )
    
    deslocamento = (
        pagina - 1
    ) * por_pagina

    total_itens = contar_itens_catalogo(
        conexao,
    )

    total_paginas = (
        total_itens + por_pagina - 1
    ) // por_pagina

    registros = listar_itens_catalogo(
        conexao,
        limite=por_pagina,
        deslocamento=deslocamento,
        ordenacao=ordenacao,
    )

    itens = [
        converter_item_catalogo(registro)
        for registro in registros
    ]

    return PaginaItensCatalogoDTO(
        itens=itens,
        pagina=pagina,
        por_pagina=por_pagina,
        total_itens=total_itens,
        total_paginas=total_paginas,
        tem_anterior=pagina > 1,
        tem_proxima=pagina < total_paginas,
    )