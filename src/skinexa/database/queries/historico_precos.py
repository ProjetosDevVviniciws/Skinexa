from datetime import datetime
from decimal import Decimal

from sqlalchemy import text, bindparam
from sqlalchemy.engine import Connection

def obter_item_catalogo_id_por_nome_mercado(
    conexao: Connection,
    nome_mercado: str,
) -> int | None:
    """
    Obtém o ID de um item do catálogo
    a partir do nome de mercado.
    """

    consulta = text(
        """
        SELECT id
        FROM itens_catalogo
        WHERE nome_mercado = :nome_mercado
        LIMIT 1
        """
    )

    resultado = conexao.execute(
        consulta,
        {
            "nome_mercado": nome_mercado,
        },
    ).scalar_one_or_none()

    if resultado is None:
        return None

    return int(resultado)

def obter_itens_catalogo_ids_por_nomes_mercado(
    conexao: Connection,
    nomes_mercado: set[str],
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
        WHERE nome_mercado IN :nomes_mercado
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
            "nomes_mercado": tuple(
                nomes_mercado
            ),
        },
    )

    return {
        str(registro.nome_mercado): int(registro.id)
        for registro in resultado
    }

def obter_plataforma_mercado_id_por_identificador(
    conexao: Connection,
    identificador: str,
) -> int | None:
    """
    Obtém o ID de uma plataforma de mercado
    a partir do identificador interno.
    """

    consulta = text(
        """
        SELECT id
        FROM plataformas_mercado
        WHERE identificador = :identificador
          AND ativa = 1
        LIMIT 1
        """
    )

    resultado = conexao.execute(
        consulta,
        {
            "identificador": identificador,
        },
    ).scalar_one_or_none()

    if resultado is None:
        return None

    return int(resultado)


def inserir_historico_preco(
    conexao: Connection,
    *,
    item_catalogo_id: int,
    plataforma_mercado_id: int,
    moeda: str,
    menor_preco: Decimal | None,
    maior_preco: Decimal | None,
    preco_medio: Decimal | None,
    preco_mediano: Decimal | None,
    maior_ordem_compra: Decimal | None,
    quantidade_anuncios: int | None,
    volume_vendas: int | None,
    atualizado_na_origem_em: datetime | None,
) -> int:
    """
    Registra uma nova coleta de preço no histórico.

    Retorna o ID da linha criada.
    """

    consulta = text(
        """
        INSERT INTO historico_precos (
            item_catalogo_id,
            plataforma_mercado_id,
            moeda,
            menor_preco,
            maior_preco,
            preco_medio,
            preco_mediano,
            maior_ordem_compra,
            quantidade_anuncios,
            volume_vendas,
            atualizado_na_origem_em
        )
        VALUES (
            :item_catalogo_id,
            :plataforma_mercado_id,
            :moeda,
            :menor_preco,
            :maior_preco,
            :preco_medio,
            :preco_mediano,
            :maior_ordem_compra,
            :quantidade_anuncios,
            :volume_vendas,
            :atualizado_na_origem_em
        )
        """
    )

    parametros = {
        "item_catalogo_id": item_catalogo_id,
        "plataforma_mercado_id": plataforma_mercado_id,
        "moeda": moeda,
        "menor_preco": menor_preco,
        "maior_preco": maior_preco,
        "preco_medio": preco_medio,
        "preco_mediano": preco_mediano,
        "maior_ordem_compra": maior_ordem_compra,
        "quantidade_anuncios": quantidade_anuncios,
        "volume_vendas": volume_vendas,
        "atualizado_na_origem_em": (
            atualizado_na_origem_em
        ),
    }

    resultado = conexao.execute(
        consulta,
        parametros,
    )

    historico_id = resultado.lastrowid

    if historico_id is None:
        raise RuntimeError(
            "O banco não retornou o ID do histórico de preço."
        )

    return int(historico_id)

def obter_ultimos_precos_itens_plataforma(
    conexao: Connection,
    *,
    item_catalogo_ids: set[int],
    plataforma_mercado_id: int,
) -> dict[int, dict[str, object]]:
    """
    Obtém o preço mais recente de cada item
    para uma determinada plataforma.

    O registro mais recente é definido por
    coletado_em e, em caso de empate, pelo id.
    """

    if not item_catalogo_ids:
        return {}

    consulta = text(
        """
        SELECT
            historico.item_catalogo_id,
            historico.moeda,
            historico.menor_preco,
            historico.maior_preco,
            historico.preco_medio,
            historico.preco_mediano,
            historico.maior_ordem_compra,
            historico.quantidade_anuncios,
            historico.volume_vendas,
            historico.coletado_em,
            historico.atualizado_na_origem_em
        FROM (
            SELECT
                hp.*,
                ROW_NUMBER() OVER (
                    PARTITION BY hp.item_catalogo_id
                    ORDER BY
                        hp.coletado_em DESC,
                        hp.id DESC
                ) AS posicao
            FROM historico_precos AS hp
            WHERE
                hp.plataforma_mercado_id =
                    :plataforma_mercado_id
                AND hp.item_catalogo_id
                    IN :item_catalogo_ids
        ) AS historico
        WHERE historico.posicao = 1
        """
    ).bindparams(
        bindparam(
            "item_catalogo_ids",
            expanding=True,
        )
    )

    resultado = conexao.execute(
        consulta,
        {
            "item_catalogo_ids": tuple(
                item_catalogo_ids
            ),
            "plataforma_mercado_id": (
                plataforma_mercado_id
            ),
        },
    )

    return {
        int(registro.item_catalogo_id): {
            "moeda": registro.moeda,
            "menor_preco": registro.menor_preco,
            "maior_preco": registro.maior_preco,
            "preco_medio": registro.preco_medio,
            "preco_mediano": registro.preco_mediano,
            "maior_ordem_compra": (
                registro.maior_ordem_compra
            ),
            "quantidade_anuncios": (
                registro.quantidade_anuncios
            ),
            "volume_vendas": registro.volume_vendas,
            "coletado_em": registro.coletado_em,
            "atualizado_na_origem_em": (
                registro.atualizado_na_origem_em
            ),
        }
        for registro in resultado
    }