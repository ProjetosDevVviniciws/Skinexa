from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Connection

def obter_conteiner_catalogo_por_id_externo(
    conexao: Connection,
    *,
    fonte: str,
    id_externo: str,
) -> dict[str, Any] | None:
    """Obtém um contêiner por sua identidade externa."""

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
            item_catalogo_id,
            nome,
            tipo_conteiner,
            url_imagem,
            criado_em,
            atualizado_em
        FROM conteineres_catalogo
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

def inserir_ou_atualizar_conteiner_catalogo(
    conexao: Connection,
    *,
    fonte: str,
    id_externo: str,
    nome: str,
    item_catalogo_id: int | None = None,
    tipo_conteiner: str | None = None,
    url_imagem: str | None = None,
) -> int:
    """
    Insere ou atualiza um contêiner sem duplicações.

    Preserva informações opcionais existentes quando
    a nova importação não fornecer esses valores.

    Retorna o identificador interno do contêiner.
    """

    fonte_normalizada = fonte.strip()
    id_normalizado = id_externo.strip()
    nome_normalizado = nome.strip()

    if not fonte_normalizada:
        raise ValueError(
            "A fonte do contêiner não pode ser vazia."
        )

    if not id_normalizado:
        raise ValueError(
            "O ID externo do contêiner não pode ser vazio."
        )

    if not nome_normalizado:
        raise ValueError(
            "O nome do contêiner não pode ser vazio."
        )

    if (
        item_catalogo_id is not None
        and item_catalogo_id <= 0
    ):
        raise ValueError(
            "O ID do item comercial deve ser maior que zero."
        )

    tipo_normalizado = (
        tipo_conteiner.strip()
        if tipo_conteiner is not None
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
        INSERT INTO conteineres_catalogo (
            fonte,
            id_externo,
            item_catalogo_id,
            nome,
            tipo_conteiner,
            url_imagem
        )
        VALUES (
            :fonte,
            :id_externo,
            :item_catalogo_id,
            :nome,
            :tipo_conteiner,
            :url_imagem
        )
        ON DUPLICATE KEY UPDATE
            id = LAST_INSERT_ID(id),
            item_catalogo_id = COALESCE(
                VALUES(item_catalogo_id),
                item_catalogo_id
            ),
            nome = VALUES(nome),
            tipo_conteiner = COALESCE(
                VALUES(tipo_conteiner),
                tipo_conteiner
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
            "item_catalogo_id": item_catalogo_id,
            "nome": nome_normalizado,
            "tipo_conteiner": tipo_normalizado,
            "url_imagem": imagem_normalizada,
        },
    )

    conteiner_id = resultado.lastrowid

    if conteiner_id is None or conteiner_id <= 0:
        raise RuntimeError(
            "Não foi possível obter o ID do contêiner."
        )

    return int(conteiner_id)

def contar_conteineres_catalogo(
    conexao: Connection,
) -> int:
    """Retorna a quantidade total de contêineres cadastrados."""

    consulta = text(
        """
        SELECT COUNT(*)
        FROM conteineres_catalogo
        """
    )

    resultado = conexao.execute(
        consulta
    ).scalar_one()

    return int(resultado)