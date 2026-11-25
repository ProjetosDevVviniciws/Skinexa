"""Serviços de persistência das coleções do catálogo."""

from sqlalchemy.engine import Connection

from skinexa.database.queries.colecoes_catalogo import (
    inserir_ou_atualizar_colecao_catalogo,
)

from skinexa.dto.catalogo.colecoes import (
    ColecaoCatalogoDTO,
)

def persistir_colecao_catalogo(
    conexao: Connection,
    colecao: ColecaoCatalogoDTO,
) -> int:
    """
    Persiste uma coleção normalizada no catálogo.

    Insere ou atualiza a coleção utilizando sua identidade
    externa (fonte, id_externo).

    Retorna o identificador interno da coleção.

    A conexão e a transação são controladas pelo chamador.
    """

    return inserir_ou_atualizar_colecao_catalogo(
        conexao,
        fonte=colecao.fonte,
        id_externo=colecao.id_externo,
        nome=colecao.nome,
        tipo_colecao=colecao.tipo_colecao,
        url_imagem=colecao.url_imagem,
    )