"""Queries relacionadas ao catálogo de itens do Skinexa."""

from typing import Any

from sqlalchemy import bindparam, text

from sqlalchemy.engine import Connection

import json

from skinexa.dto.catalogo.importacao import (
    ItemImportacaoCatalogoDTO,
)

ORDENACOES_CATALOGO = {
    "nome_asc": "nome_exibicao ASC, id ASC",
    "nome_desc": "nome_exibicao DESC, id DESC",
    "mais_recentes": "criado_em DESC, id DESC",
    "mais_antigos": "criado_em ASC, id ASC",
}

def _obter_ordenacao_catalogo(
    ordenacao: str,
) -> str:
    """Obtém a cláusula de ordenação permitida do catálogo."""

    try:
        return ORDENACOES_CATALOGO[ordenacao]
    except KeyError as erro:
        raise ValueError(
            "Ordenação de catálogo inválida."
        ) from erro

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

def pesquisar_itens_catalogo_por_nome(
    conexao: Connection,
    *,
    termo: str,
    limite: int,
    deslocamento: int,
) -> list[dict[str, Any]]:
    """Pesquisa itens do catálogo por nome."""

    termo_normalizado = termo.strip()

    if not termo_normalizado:
        return []

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
        WHERE
            nome_mercado LIKE :termo
            OR nome_exibicao LIKE :termo
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
            "termo": f"%{termo_normalizado}%",
            "limite": limite,
            "deslocamento": deslocamento,
        },
    )

    return [
        dict(registro._mapping)
        for registro in resultado
    ]

def listar_itens_catalogo(
    conexao: Connection,
    *,
    limite: int,
    deslocamento: int,
    ordenacao: str = "nome_asc",
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

    clausula_ordenacao = (
        _obter_ordenacao_catalogo(
            ordenacao,
        )
    )
    
    consulta = text(
        f"""
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
        ORDER BY {clausula_ordenacao}
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

def buscar_sugestoes_itens_catalogo(
    conexao: Connection,
    *,
    termo: str,
    limite: int = 10,
) -> list[dict[str, Any]]:
    """Busca sugestões de itens para autocomplete."""

    termo_normalizado = termo.strip()

    if len(termo_normalizado) < 2:
        return []

    if limite < 1:
        raise ValueError(
            "O limite deve ser maior que zero."
        )

    consulta = text(
        """
        SELECT
            id,
            nome_mercado,
            nome_exibicao,
            tipo_item,
            COALESCE(
                NULLIF(url_icone, ''),
                NULLIF(url_icone_grande, '')
            ) AS url_icone
        FROM itens_catalogo
        WHERE
            nome_mercado LIKE :termo
            OR nome_exibicao LIKE :termo
        ORDER BY
            CASE
                WHEN nome_exibicao LIKE :prefixo THEN 0
                WHEN nome_mercado LIKE :prefixo THEN 1
                ELSE 2
            END,
            nome_exibicao ASC,
            id ASC
        LIMIT :limite
        """
    )

    resultado = conexao.execute(
        consulta,
        {
            "termo": f"%{termo_normalizado}%",
            "prefixo": f"{termo_normalizado}%",
            "limite": limite,
        },
    )

    return [
        dict(registro._mapping)
        for registro in resultado
    ]
     
def filtrar_itens_catalogo(
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
) -> list[dict[str, Any]]:
    """Filtra itens do catálogo por características."""

    if limite < 1:
        raise ValueError(
            "O limite deve ser maior que zero."
        )

    if deslocamento < 0:
        raise ValueError(
            "O deslocamento não pode ser negativo."
        )

    filtros = []
    parametros: dict[str, Any] = {
        "limite": limite,
        "deslocamento": deslocamento,
    }

    clausula_ordenacao = (
        _obter_ordenacao_catalogo(
            ordenacao,
        )
    )

    if tipo_item is not None:
        tipo_item_normalizado = tipo_item.strip()

        if tipo_item_normalizado:
            filtros.append(
                "tipo_item = :tipo_item"
            )
            parametros["tipo_item"] = (
                tipo_item_normalizado
            )

    if nome_arma is not None:
        nome_arma_normalizado = nome_arma.strip()

        if nome_arma_normalizado:
            filtros.append(
                "nome_arma = :nome_arma"
            )
            parametros["nome_arma"] = (
                nome_arma_normalizado
            )

    if nome_acabamento is not None:
        nome_acabamento_normalizado = (
            nome_acabamento.strip()
        )

        if nome_acabamento_normalizado:
            filtros.append(
                "nome_acabamento = :nome_acabamento"
            )
            parametros["nome_acabamento"] = (
                nome_acabamento_normalizado
            )
    
    if estado_exterior is not None:
        estado_exterior_normalizado = (
            estado_exterior.strip()
        )

        if estado_exterior_normalizado:
            filtros.append(
                "estado_exterior = :estado_exterior"
            )
            parametros["estado_exterior"] = (
                estado_exterior_normalizado
            )

    if raridade is not None:
        raridade_normalizada = raridade.strip()

        if raridade_normalizada:
            filtros.append(
                "raridade = :raridade"
            )
            parametros["raridade"] = (
                raridade_normalizada
            )

    if colecao is not None:
        colecao_normalizada = colecao.strip()

        if colecao_normalizada:
            filtros.append(
                "colecao = :colecao"
            )
            parametros["colecao"] = (
                colecao_normalizada
            )
    
    if variante_stattrak is not None:
        filtros.append(
            "variante_stattrak = :variante_stattrak"
        )
        parametros["variante_stattrak"] = (
            variante_stattrak
        )

    if variante_souvenir is not None:
        filtros.append(
            "variante_souvenir = :variante_souvenir"
        )
        parametros["variante_souvenir"] = (
            variante_souvenir
        )

    clausula_where = ""

    if filtros:
        clausula_where = (
            "WHERE " + " AND ".join(filtros)
        )

    consulta = text(
        f"""
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
        {clausula_where}
        ORDER BY {clausula_ordenacao}
        LIMIT :limite
        OFFSET :deslocamento
        """
    )

    resultado = conexao.execute(
        consulta,
        parametros,
    )

    return [
        dict(registro._mapping)
        for registro in resultado
    ]
    
def inserir_ou_atualizar_item_catalogo_importacao(
    conexao: Connection,
    item: ItemImportacaoCatalogoDTO,
) -> int:
    """
    Insere um item comercial ou preserva o registro existente.

    Retorna o identificador interno do item no catálogo.
    """

    if item.app_id <= 0:
        raise ValueError(
            "O app_id deve ser maior que zero."
        )

    if not item.nome_mercado.strip():
        raise ValueError(
            "O nome de mercado não pode ser vazio."
        )

    if not item.nome_exibicao.strip():
        raise ValueError(
            "O nome de exibição não pode ser vazio."
        )

    if not item.tipo_item.strip():
        raise ValueError(
            "O tipo do item não pode ser vazio."
        )

    consulta = text(
        """
        INSERT INTO itens_catalogo (
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
        )
        VALUES (
            :app_id,
            :nome_mercado,
            :nome_exibicao,
            :tipo_item,
            :nome_arma,
            :nome_acabamento,
            :estado_exterior,
            :raridade,
            :qualidade,
            :colecao,
            :descricao,
            :indice_pintura,
            :float_minimo,
            :float_maximo,
            :variante_stattrak,
            :variante_souvenir,
            :comercializavel,
            :mercadoria_generica,
            :steam_class_id,
            :steam_instance_id,
            :url_icone,
            :url_icone_grande,
            :tags,
            :metadados_origem
        )
        ON DUPLICATE KEY UPDATE
            id = LAST_INSERT_ID(id),
            nome_arma = COALESCE(
                nome_arma,
                VALUES(nome_arma)
            ),
            nome_acabamento = COALESCE(
                nome_acabamento,
                VALUES(nome_acabamento)
            ),
            estado_exterior = COALESCE(
                estado_exterior,
                VALUES(estado_exterior)
            ),
            raridade = COALESCE(
                raridade,
                VALUES(raridade)
            ),
            qualidade = COALESCE(
                qualidade,
                VALUES(qualidade)
            ),
            colecao = COALESCE(
                colecao,
                VALUES(colecao)
            ),
            descricao = COALESCE(
                descricao,
                VALUES(descricao)
            ),
            float_minimo = COALESCE(
                float_minimo,
                VALUES(float_minimo)
            ),
            float_maximo = COALESCE(
                float_maximo,
                VALUES(float_maximo)
            ),
            url_icone_grande = COALESCE(
                url_icone_grande,
                VALUES(url_icone_grande)
            )
        """
    )

    parametros = {
        "app_id": item.app_id,
        "nome_mercado": item.nome_mercado,
        "nome_exibicao": item.nome_exibicao,
        "tipo_item": item.tipo_item,
        "nome_arma": item.nome_arma,
        "nome_acabamento": item.nome_acabamento,
        "estado_exterior": item.estado_exterior,
        "raridade": item.raridade,
        "qualidade": item.qualidade,
        "colecao": item.colecao,
        "descricao": item.descricao,
        "indice_pintura": None,
        "float_minimo": item.float_minimo,
        "float_maximo": item.float_maximo,
        "variante_stattrak": int(item.variante_stattrak),
        "variante_souvenir": int(item.variante_souvenir),
        "comercializavel": int(item.comercializavel),
        "mercadoria_generica": int(item.mercadoria_generica),
        "steam_class_id": item.steam_class_id,
        "steam_instance_id": item.steam_instance_id,
        "url_icone": item.url_icone,
        "url_icone_grande": item.url_icone_grande,
        "tags": (
            json.dumps(item.tags, ensure_ascii=False)
            if item.tags is not None
            else None
        ),
        "metadados_origem": (
            json.dumps(
                item.metadados_origem,
                ensure_ascii=False,
            )
            if item.metadados_origem is not None
            else None
        ),
    }

    resultado = conexao.execute(
        consulta,
        parametros,
    )

    item_catalogo_id = resultado.lastrowid

    if item_catalogo_id is None or item_catalogo_id <= 0:
        raise RuntimeError(
            "Não foi possível obter o ID do item importado."
        )

    return int(item_catalogo_id)


def pesquisar_itens_catalogo_paginados(
    conexao: Connection,
    *,
    termo: str,
    limite: int,
    deslocamento: int,
    ordenacao: str = "nome_asc",
    tipo_item: str | None = None,
    nome_arma: str | None = None,
    nome_acabamento: str | None = None,
    estado_exterior: str | None = None,
    raridade: str | None = None,
    colecao: str | None = None,
    variante_stattrak: bool | None = None,
    variante_souvenir: bool | None = None,
) -> tuple[list[dict[str, Any]], int]:
    """
    Pesquisa itens por nome ou identificador e aplica
    filtros opcionais, com paginação e contagem total.
    """

    if limite < 1:
        raise ValueError(
            "O limite deve ser maior que zero."
        )

    if deslocamento < 0:
        raise ValueError(
            "O deslocamento não pode ser negativo."
        )

    clausula_ordenacao = _obter_ordenacao_catalogo(
        ordenacao
    )

    termo_normalizado = termo.strip()

    filtros_textuais = {
        "tipo_item": tipo_item,
        "nome_arma": nome_arma,
        "nome_acabamento": nome_acabamento,
        "estado_exterior": estado_exterior,
        "raridade": raridade,
        "colecao": colecao,
    }

    condicoes: list[str] = []
    parametros: dict[str, Any] = {}

    # Pesquisa por nome ou identificador interno.
    if termo_normalizado:
        identificador = (
            int(termo_normalizado)
            if termo_normalizado.isascii()
            and termo_normalizado.isdecimal()
            else 0
        )

        condicoes.append(
            """
            (
                nome_mercado LIKE :termo
                OR nome_exibicao LIKE :termo
                OR id = :identificador
            )
            """
        )

        parametros["termo"] = f"%{termo_normalizado}%"
        parametros["identificador"] = identificador

    # Filtros textuais opcionais.
    for campo, valor in filtros_textuais.items():
        if valor is None:
            continue

        valor_normalizado = valor.strip()

        if not valor_normalizado:
            continue

        # Os nomes das colunas são fixos e definidos
        # internamente, nunca recebidos da requisição.
        condicoes.append(
            f"{campo} = :{campo}"
        )

        parametros[campo] = valor_normalizado

    # Filtros booleanos opcionais.
    if variante_stattrak is not None:
        condicoes.append(
            "variante_stattrak = :variante_stattrak"
        )

        parametros["variante_stattrak"] = (
            variante_stattrak
        )

    if variante_souvenir is not None:
        condicoes.append(
            "variante_souvenir = :variante_souvenir"
        )

        parametros["variante_souvenir"] = (
            variante_souvenir
        )

    # Preserva o comportamento anterior para
    # chamadas sem termo e sem filtros.
    if not condicoes:
        return [], 0

    clausula_where = (
        "WHERE " + " AND ".join(condicoes)
    )

    consulta_total = text(
        f"""
        SELECT COUNT(*)
        FROM itens_catalogo
        {clausula_where}
        """
    )

    total_itens = int(
        conexao.execute(
            consulta_total,
            parametros,
        ).scalar_one()
    )

    consulta_itens = text(
        f"""
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
        {clausula_where}
        ORDER BY {clausula_ordenacao}
        LIMIT :limite
        OFFSET :deslocamento
        """
    )

    registros = conexao.execute(
        consulta_itens,
        {
            **parametros,
            "limite": limite,
            "deslocamento": deslocamento,
        },
    )

    return (
        [
            dict(registro._mapping)
            for registro in registros
        ],
        total_itens,
    )
    
def obter_itens_catalogo_ids_por_skin_ids(
    conexao: Connection,
    skin_ids: set[str],
    *,
    app_id: int = 730,
) -> dict[str, list[int]]:
    """
    Resolve IDs comerciais a partir dos skin_ids da CSGO-API.

    Um skin_id pode corresponder a vários itens comerciais.

    Retorna um dicionário contendo somente os skin_ids
    encontrados e seus respectivos IDs internos, sem
    duplicações e em ordem crescente.

    Não modifica os registros existentes.
    """

    if app_id <= 0:
        raise ValueError(
            "O app_id deve ser maior que zero."
        )

    ids_normalizados: set[str] = set()

    for skin_id in skin_ids:
        if not isinstance(skin_id, str):
            raise ValueError(
                "Todos os skin_ids devem ser strings."
            )

        identificador = skin_id.strip()

        if identificador:
            ids_normalizados.add(identificador)

    if not ids_normalizados:
        return {}

    consulta = text(
        """
        SELECT
            id,
            CASE
                WHEN JSON_VALID(metadados_origem)
                THEN JSON_UNQUOTE(
                    JSON_EXTRACT(
                        metadados_origem,
                        '$.skin_id'
                    )
                )
                ELSE NULL
            END AS skin_id
        FROM itens_catalogo
        WHERE app_id = :app_id
          AND CASE
                WHEN JSON_VALID(metadados_origem)
                THEN JSON_UNQUOTE(
                    JSON_EXTRACT(
                        metadados_origem,
                        '$.fonte'
                    )
                )
                ELSE NULL
              END = :fonte
          AND CASE
                WHEN JSON_VALID(metadados_origem)
                THEN JSON_UNQUOTE(
                    JSON_EXTRACT(
                        metadados_origem,
                        '$.skin_id'
                    )
                )
                ELSE NULL
              END IN :skin_ids
        """
    ).bindparams(
        bindparam(
            "skin_ids",
            expanding=True,
        )
    )

    resultado = conexao.execute(
        consulta,
        {
            "app_id": app_id,
            "fonte": "csgo_api",
            "skin_ids": tuple(sorted(ids_normalizados)),
        },
    )

    mapa: dict[str, set[int]] = {}

    for registro in resultado.mappings():
        skin_id = registro["skin_id"]
        item_id = int(registro["id"])

        if skin_id not in ids_normalizados:
            continue

        if item_id <= 0:
            raise RuntimeError(
                "ID comercial inválido encontrado "
                f"para a skin {skin_id}."
            )

        mapa.setdefault(
            skin_id,
            set(),
        ).add(item_id)

    return {
        skin_id: sorted(ids)
        for skin_id, ids in sorted(mapa.items())
    }