from typing import Any

from sqlalchemy import Connection, text

def inserir_ou_atualizar_conteudo_conteiner_catalogo(
    conexao: Connection,
    *,
    conteiner_catalogo_id: int,
    fonte: str,
    id_externo_conteudo: str,
    nome_conteudo: str,
    tipo_conteudo: str,
    raridade: str | None = None,
    indice_pintura: int | None = None,
    nome_fase: str | None = None,
    url_imagem: str | None = None,
) -> int:
    """
    Insere ou atualiza um conteúdo de contêiner.

    A identidade é definida pelo contêiner, fonte,
    identificador externo e tipo do conteúdo.

    Retorna o identificador interno do conteúdo.
    """

    if conteiner_catalogo_id <= 0:
        raise ValueError(
            "O ID do contêiner deve ser maior que zero."
        )

    fonte_normalizada = fonte.strip()
    id_normalizado = id_externo_conteudo.strip()
    nome_normalizado = nome_conteudo.strip()
    tipo_normalizado = tipo_conteudo.strip()

    if not fonte_normalizada:
        raise ValueError(
            "A fonte do conteúdo não pode ser vazia."
        )

    if not id_normalizado:
        raise ValueError(
            "O ID externo do conteúdo não pode ser vazio."
        )

    if not nome_normalizado:
        raise ValueError(
            "O nome do conteúdo não pode ser vazio."
        )

    if tipo_normalizado not in (
        "contains",
        "contains_rare",
    ):
        raise ValueError(
            "O tipo do conteúdo deve ser contains "
            "ou contains_rare."
        )

    if indice_pintura is not None and indice_pintura < 0:
        raise ValueError(
            "O índice de pintura não pode ser negativo."
        )

    raridade_normalizada = (
        raridade.strip() or None
        if raridade is not None
        else None
    )

    fase_normalizada = (
        nome_fase.strip() or None
        if nome_fase is not None
        else None
    )

    imagem_normalizada = (
        url_imagem.strip() or None
        if url_imagem is not None
        else None
    )

    consulta = text(
        """
        INSERT INTO conteudos_conteineres_catalogo (
            conteiner_catalogo_id,
            fonte,
            id_externo_conteudo,
            nome_conteudo,
            tipo_conteudo,
            raridade,
            indice_pintura,
            nome_fase,
            url_imagem
        )
        VALUES (
            :conteiner_catalogo_id,
            :fonte,
            :id_externo_conteudo,
            :nome_conteudo,
            :tipo_conteudo,
            :raridade,
            :indice_pintura,
            :nome_fase,
            :url_imagem
        )
        ON DUPLICATE KEY UPDATE
            id = LAST_INSERT_ID(id),
            nome_conteudo = VALUES(nome_conteudo),
            raridade = COALESCE(
                VALUES(raridade),
                raridade
            ),
            indice_pintura = COALESCE(
                VALUES(indice_pintura),
                indice_pintura
            ),
            nome_fase = COALESCE(
                VALUES(nome_fase),
                nome_fase
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
            "conteiner_catalogo_id": conteiner_catalogo_id,
            "fonte": fonte_normalizada,
            "id_externo_conteudo": id_normalizado,
            "nome_conteudo": nome_normalizado,
            "tipo_conteudo": tipo_normalizado,
            "raridade": raridade_normalizada,
            "indice_pintura": indice_pintura,
            "nome_fase": fase_normalizada,
            "url_imagem": imagem_normalizada,
        },
    )

    conteudo_id = resultado.lastrowid

    if conteudo_id is None or conteudo_id <= 0:
        raise RuntimeError(
            "Não foi possível obter o ID do conteúdo."
        )

    return int(conteudo_id)

def listar_conteudos_por_conteiner_catalogo(
    conexao: Connection,
    *,
    conteiner_catalogo_id: int,
) -> list[dict[str, Any]]:
    """Lista os conteúdos associados a um contêiner."""

    if conteiner_catalogo_id <= 0:
        return []

    consulta = text(
        """
        SELECT
            id,
            conteiner_catalogo_id,
            fonte,
            id_externo_conteudo,
            nome_conteudo,
            tipo_conteudo,
            raridade,
            indice_pintura,
            nome_fase,
            url_imagem,
            criado_em,
            atualizado_em
        FROM conteudos_conteineres_catalogo
        WHERE conteiner_catalogo_id = :conteiner_catalogo_id
        ORDER BY
            tipo_conteudo ASC,
            nome_conteudo ASC,
            id ASC
        """
    )

    resultado = conexao.execute(
        consulta,
        {
            "conteiner_catalogo_id": conteiner_catalogo_id,
        },
    )

    return [
        dict(registro._mapping)
        for registro in resultado
    ]

def contar_conteudos_conteineres_catalogo(
    conexao: Connection,
) -> int:
    """Retorna a quantidade total de conteúdos cadastrados."""

    consulta = text(
        """
        SELECT COUNT(*)
        FROM conteudos_conteineres_catalogo
        """
    )

    resultado = conexao.execute(
        consulta
    ).scalar_one()

    return int(resultado)