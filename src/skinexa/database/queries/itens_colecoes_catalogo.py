from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Connection

def inserir_ou_preservar_relacao_item_colecao(
    conexao: Connection,
    *,
    item_catalogo_id: int,
    colecao_catalogo_id: int,
    fonte_relacao: str,
) -> None:
    """
    Insere uma associação entre item e coleção.

    Preserva a associação existente quando o par
    item/coleção já está cadastrado.
    """

    if item_catalogo_id <= 0:
        raise ValueError(
            "O ID do item deve ser maior que zero."
        )

    if colecao_catalogo_id <= 0:
        raise ValueError(
            "O ID da coleção deve ser maior que zero."
        )

    fonte_normalizada = fonte_relacao.strip()

    if not fonte_normalizada:
        raise ValueError(
            "A fonte da relação não pode ser vazia."
        )

    consulta = text(
        """
        INSERT INTO itens_colecoes_catalogo (
            item_catalogo_id,
            colecao_catalogo_id,
            fonte_relacao
        )
        VALUES (
            :item_catalogo_id,
            :colecao_catalogo_id,
            :fonte_relacao
        )
        ON DUPLICATE KEY UPDATE
            fonte_relacao = fonte_relacao
        """
    )

    conexao.execute(
        consulta,
        {
            "item_catalogo_id": item_catalogo_id,
            "colecao_catalogo_id": colecao_catalogo_id,
            "fonte_relacao": fonte_normalizada,
        },
    )

def listar_colecoes_por_item_catalogo(
    conexao: Connection,
    *,
    item_catalogo_id: int,
) -> list[dict[str, Any]]:
    """Lista as coleções vinculadas a um item comercial."""

    if item_catalogo_id <= 0:
        return []

    consulta = text(
        """
        SELECT
            c.id,
            c.fonte,
            c.id_externo,
            c.nome,
            c.tipo_colecao,
            c.url_imagem,
            ic.fonte_relacao,
            ic.criado_em AS relacao_criada_em
        FROM itens_colecoes_catalogo AS ic
        INNER JOIN colecoes_catalogo AS c
            ON c.id = ic.colecao_catalogo_id
        WHERE ic.item_catalogo_id = :item_catalogo_id
        ORDER BY
            c.nome ASC,
            c.id ASC
        """
    )

    resultado = conexao.execute(
        consulta,
        {
            "item_catalogo_id": item_catalogo_id,
        },
    )

    return [
        dict(registro._mapping)
        for registro in resultado
    ]

def contar_relacoes_itens_colecoes_catalogo(
    conexao: Connection,
) -> int:
    """Retorna a quantidade total de associações cadastradas."""

    consulta = text(
        """
        SELECT COUNT(*)
        FROM itens_colecoes_catalogo
        """
    )

    resultado = conexao.execute(
        consulta
    ).scalar_one()

    return int(resultado)