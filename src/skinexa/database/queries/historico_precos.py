from datetime import datetime
from decimal import Decimal

from sqlalchemy import text
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