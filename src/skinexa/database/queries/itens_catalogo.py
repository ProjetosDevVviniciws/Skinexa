import json

from sqlalchemy import text
from sqlalchemy.engine import Connection

from skinexa.dto.steam.inventario import ItemCatalogoSteamDTO

def salvar_item_catalogo(
    conexao: Connection,
    item: ItemCatalogoSteamDTO,
) -> int:
    """
    Cria ou atualiza um item do catálogo.

    Retorna o ID da linha criada ou já existente.
    """

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
            trocavel,
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
            :trocavel,
            :mercadoria_generica,
            :steam_class_id,
            :steam_instance_id,
            :url_icone,
            :url_icone_grande,
            CAST(:tags AS JSON),
            CAST(:metadados_origem AS JSON)
        )
        ON DUPLICATE KEY UPDATE
            id = LAST_INSERT_ID(id),
            nome_exibicao = VALUES(nome_exibicao),
            tipo_item = VALUES(tipo_item),
            nome_arma = VALUES(nome_arma),
            nome_acabamento = VALUES(nome_acabamento),
            estado_exterior = VALUES(estado_exterior),
            raridade = VALUES(raridade),
            qualidade = VALUES(qualidade),
            colecao = VALUES(colecao),
            descricao = VALUES(descricao),
            indice_pintura = VALUES(indice_pintura),
            float_minimo = VALUES(float_minimo),
            float_maximo = VALUES(float_maximo),
            variante_stattrak = VALUES(variante_stattrak),
            variante_souvenir = VALUES(variante_souvenir),
            comercializavel = VALUES(comercializavel),
            trocavel = VALUES(trocavel),
            mercadoria_generica = VALUES(mercadoria_generica),
            steam_class_id = VALUES(steam_class_id),
            steam_instance_id = VALUES(steam_instance_id),
            url_icone = VALUES(url_icone),
            url_icone_grande = VALUES(url_icone_grande),
            tags = VALUES(tags),
            metadados_origem = VALUES(metadados_origem)
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
        "indice_pintura": item.indice_pintura,
        "float_minimo": item.float_minimo,
        "float_maximo": item.float_maximo,
        "variante_stattrak": int(item.variante_stattrak),
        "variante_souvenir": int(item.variante_souvenir),
        "comercializavel": int(item.comercializavel),
        "trocavel": int(item.trocavel),
        "mercadoria_generica": int(
            item.mercadoria_generica
        ),
        "steam_class_id": item.steam_class_id,
        "steam_instance_id": item.steam_instance_id,
        "url_icone": item.url_icone,
        "url_icone_grande": item.url_icone_grande,
        "tags": json.dumps(
            list(item.tags),
            ensure_ascii=False,
        ),
        "metadados_origem": json.dumps(
            item.metadados_origem,
            ensure_ascii=False,
        ),
    }

    resultado = conexao.execute(
        consulta,
        parametros,
    )

    item_id = resultado.lastrowid

    if item_id is None:
        raise RuntimeError(
            "O banco não retornou o ID do item do catálogo."
        )

    return int(item_id)