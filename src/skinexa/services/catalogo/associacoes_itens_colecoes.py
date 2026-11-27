"""Orquestração das associações entre coleções e itens comerciais."""

from sqlalchemy.engine import Connection

from skinexa.database.queries.itens_catalogo import (
    obter_itens_catalogo_ids_por_skin_ids,
)

from skinexa.dto.catalogo.colecoes import (
    ColecaoCatalogoDTO,
    RelacaoItemColecaoDTO,
)

from skinexa.services.catalogo.colecoes import (
    persistir_colecao_catalogo,
)

from skinexa.services.catalogo.relacionamentos import (
    persistir_relacao_item_colecao,
)

def associar_itens_colecao_catalogo(
    conexao: Connection,
    colecao: ColecaoCatalogoDTO,
    skin_ids: set[str],
) -> tuple[int, int, int]:
    """
    Associa itens comerciais existentes a uma coleção.

    Retorna:
        - ID interno da coleção;
        - quantidade de relacionamentos processados;
        - quantidade de skin_ids sem correspondência.

    A quantidade de relacionamentos processados não
    representa necessariamente novas inserções.

    A conexão e a transação são controladas pelo chamador.
    """

    if not isinstance(skin_ids, set):
        raise ValueError(
            "Os skin_ids devem ser fornecidos como um conjunto."
        )

    ids_normalizados: set[str] = set()

    for skin_id in skin_ids:
        if not isinstance(skin_id, str):
            raise ValueError(
                "Todos os skin_ids devem ser strings."
            )

        identificador = skin_id.strip()

        if not identificador:
            raise ValueError(
                "O skin_id não pode ser vazio."
            )

        ids_normalizados.add(identificador)

    mapa_itens = obter_itens_catalogo_ids_por_skin_ids(
        conexao,
        ids_normalizados,
    )

    ids_comerciais: dict[str, list[int]] = {}

    for skin_id, ids in mapa_itens.items():
        if skin_id not in ids_normalizados:
            raise RuntimeError(
                "A consulta retornou um skin_id não solicitado."
            )

        if any(
            not isinstance(item_id, int)
            or isinstance(item_id, bool)
            or item_id <= 0
            for item_id in ids
        ):
            raise RuntimeError(
                f"IDs comerciais inválidos para {skin_id}."
            )

        ids_comerciais[skin_id] = sorted(set(ids))

    total_sem_correspondencia = sum(
        1
        for skin_id in ids_normalizados
        if not ids_comerciais.get(skin_id)
    )

    colecao_id = persistir_colecao_catalogo(
        conexao,
        colecao,
    )

    if not isinstance(colecao_id, int) or colecao_id <= 0:
        raise RuntimeError(
            "O ID interno da coleção é inválido."
        )

    itens_associados: set[int] = set()

    for skin_id in sorted(ids_normalizados):
        for item_catalogo_id in ids_comerciais.get(
            skin_id,
            [],
        ):
            if item_catalogo_id in itens_associados:
                continue

            relacao = RelacaoItemColecaoDTO(
                item_catalogo_id=item_catalogo_id,
                colecao_catalogo_id=colecao_id,
                fonte_relacao=colecao.fonte,
            )

            persistir_relacao_item_colecao(
                conexao,
                relacao,
            )

            itens_associados.add(item_catalogo_id)

    return (
        colecao_id,
        len(itens_associados),
        total_sem_correspondencia,
    )