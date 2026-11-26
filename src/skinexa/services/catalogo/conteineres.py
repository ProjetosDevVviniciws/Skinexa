"""Serviços de persistência dos contêineres do catálogo."""

from sqlalchemy.engine import Connection

from skinexa.database.queries.conteineres_catalogo import (
    inserir_ou_atualizar_conteiner_catalogo,
)

from skinexa.dto.catalogo.conteineres import (
    ConteinerCatalogoDTO,
)

def persistir_conteiner_catalogo(
    conexao: Connection,
    conteiner: ConteinerCatalogoDTO,
) -> int:
    """
    Persiste um contêiner normalizado no catálogo.

    Insere ou atualiza o contêiner utilizando sua identidade
    externa (fonte, id_externo).

    Preserva valores opcionais existentes quando o DTO
    não fornece novas informações.

    Retorna o identificador interno do contêiner.

    A conexão e a transação são controladas pelo chamador.
    """

    return inserir_ou_atualizar_conteiner_catalogo(
        conexao,
        fonte=conteiner.fonte,
        id_externo=conteiner.id_externo,
        nome=conteiner.nome,
        item_catalogo_id=conteiner.item_catalogo_id,
        tipo_conteiner=conteiner.tipo_conteiner,
        url_imagem=conteiner.url_imagem,
    )