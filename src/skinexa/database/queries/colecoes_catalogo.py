"""Queries relacionadas às coleções do catálogo do Skinexa."""

from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Connection

def obter_colecao_catalogo_por_id_externo(
    conexao: Connection,
    *,
    fonte: str,
    id_externo: str,
) -> dict[str, Any] | None:
    """Obtém uma coleção pela fonte e identificador externo."""

    fonte_normalizada = fonte.strip()
    id_normalizado = id_externo.strip()

    if not fonte_normalizada or not id_normalizado:
        return None

    consulta = text(
        """
        SELECT
            id,
            fonte,
            id_externo,
            nome,
            tipo_colecao,
            url_imagem,
            criado_em,
            atualizado_em
        FROM colecoes_catalogo
        WHERE fonte = :fonte
          AND id_externo = :id_externo
        LIMIT 1
        """
    )

    resultado = (
        conexao.execute(
            consulta,
            {
                "fonte": fonte_normalizada,
                "id_externo": id_normalizado,
            },
        )
        .mappings()
        .first()
    )

    if resultado is None:
        return None

    return dict(resultado)

def inserir_ou_atualizar_colecao_catalogo(
    conexao: Connection,
    *,
    fonte: str,
    id_externo: str,
    nome: str,
    tipo_colecao: str | None = None,
    url_imagem: str | None = None,
) -> int:
    """
    Insere ou atualiza uma coleção sem duplicá-la.

    Retorna o identificador interno da coleção.
    """

    fonte_normalizada = fonte.strip()
    id_normalizado = id_externo.strip()
    nome_normalizado = nome.strip()

    if not fonte_normalizada:
        raise ValueError(
            "A fonte da coleção não pode ser vazia."
        )

    if not id_normalizado:
        raise ValueError(
            "O ID externo da coleção não pode ser vazio."
        )

    if not nome_normalizado:
        raise ValueError(
            "O nome da coleção não pode ser vazio."
        )

    tipo_normalizado = (
        tipo_colecao.strip()
        if tipo_colecao is not None
        else None
    )

    if tipo_normalizado == "":
        tipo_normalizado = None

    imagem_normalizada = (
        url_imagem.strip()
        if url_imagem is not None
        else None
    )

    if imagem_normalizada == "":
        imagem_normalizada = None

    consulta = text(
        """
        INSERT INTO colecoes_catalogo (
            fonte,
            id_externo,
            nome,
            tipo_colecao,
            url_imagem
        )
        VALUES (
            :fonte,
            :id_externo,
            :nome,
            :tipo_colecao,
            :url_imagem
        )
        ON DUPLICATE KEY UPDATE
            id = LAST_INSERT_ID(id),
            nome = VALUES(nome),
            tipo_colecao = COALESCE(
                VALUES(tipo_colecao),
                tipo_colecao
            ),
            url_imagem = COALESCE(
                VALUES(url_imagem),
                url_imagem
            )
        """
    )

    resultado = conexao.execute(
        consulta,
        {
            "fonte": fonte_normalizada,
            "id_externo": id_normalizado,
            "nome": nome_normalizado,
            "tipo_colecao": tipo_normalizado,
            "url_imagem": imagem_normalizada,
        },
    )

    colecao_id = resultado.lastrowid

    if colecao_id is None or colecao_id <= 0:
        raise RuntimeError(
            "Não foi possível obter o ID da coleção."
        )

    return int(colecao_id)

def contar_colecoes_catalogo(
    conexao: Connection,
) -> int:
    """Retorna a quantidade de coleções cadastradas."""

    consulta = text(
        """
        SELECT COUNT(*)
        FROM colecoes_catalogo
        """
    )

    resultado = conexao.execute(
        consulta
    ).scalar_one()

    return int(resultado)