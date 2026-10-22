from sqlalchemy import text

from sqlalchemy.engine import Connection

from skinexa.dto.catalogo.variante import (
    VarianteImportacaoCatalogoDTO,
)

def inserir_ou_atualizar_variante_catalogo_importacao(
    conexao: Connection,
    *,
    item_catalogo_id: int,
    variante: VarianteImportacaoCatalogoDTO,
    proteger_vinculo: bool = False,
) -> int:
    """
    Insere ou atualiza uma variante de item do catálogo.

    Utiliza fonte e id_externo como chave de unicidade,
    preservando o identificador interno do registro.
    """

    if item_catalogo_id <= 0:
        raise ValueError(
            "O item_catalogo_id deve ser maior que zero."
        )

    if variante.app_id <= 0:
        raise ValueError(
            "O app_id deve ser maior que zero."
        )

    if not variante.nome_mercado.strip():
        raise ValueError(
            "O nome de mercado não pode ser vazio."
        )

    if not variante.fonte.strip():
        raise ValueError(
            "A fonte da variante não pode ser vazia."
        )

    if not variante.id_externo.strip():
        raise ValueError(
            "O identificador externo não pode ser vazio."
        )

    atualizacao_vinculo = (
        "item_catalogo_id = item_catalogo_id,"
        if proteger_vinculo
        else "item_catalogo_id = VALUES(item_catalogo_id),"
        )
    
    consulta = text(
        f"""
        INSERT INTO variantes_itens_catalogo (
            item_catalogo_id,
            fonte,
            id_externo,
            skin_id_externo,
            indice_pintura,
            identificador_acabamento,
            nome_variante,
            url_imagem
        )
        VALUES (
            :item_catalogo_id,
            :fonte,
            :id_externo,
            :skin_id_externo,
            :indice_pintura,
            :identificador_acabamento,
            :nome_variante,
            :url_imagem
        )
        ON DUPLICATE KEY UPDATE
            id = LAST_INSERT_ID(id),
            {atualizacao_vinculo}
            skin_id_externo = COALESCE(
                VALUES(skin_id_externo),
                skin_id_externo
            ),
            indice_pintura = COALESCE(
                VALUES(indice_pintura),
                indice_pintura
            ),
            identificador_acabamento = COALESCE(
                VALUES(identificador_acabamento),
                identificador_acabamento
            ),
            nome_variante = COALESCE(
                VALUES(nome_variante),
                nome_variante
            ),
            url_imagem = COALESCE(
                VALUES(url_imagem),
                url_imagem
            )
        """
    )

    parametros = {
        "item_catalogo_id": item_catalogo_id,
        "fonte": variante.fonte.strip(),
        "id_externo": variante.id_externo.strip(),
        "skin_id_externo": variante.skin_id_externo,
        "indice_pintura": variante.indice_pintura,
        "identificador_acabamento": (
            variante.identificador_acabamento
        ),
        "nome_variante": variante.nome_variante,
        "url_imagem": variante.url_imagem,
    }

    resultado = conexao.execute(
        consulta,
        parametros,
    )

    variante_catalogo_id = resultado.lastrowid

    if (
        variante_catalogo_id is None
        or variante_catalogo_id <= 0
    ):
        raise RuntimeError(
            "Não foi possível obter o ID da variante importada."
        )

    return int(variante_catalogo_id)