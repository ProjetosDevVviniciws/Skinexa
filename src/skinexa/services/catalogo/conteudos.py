"""Serviços de persistência dos conteúdos dos contêineres."""

from sqlalchemy.engine import Connection

from skinexa.database.queries.conteudos_conteineres_catalogo import (
    inserir_ou_atualizar_conteudo_conteiner_catalogo,
)

from skinexa.dto.catalogo.conteineres import (
    ConteudoConteinerCatalogoDTO,
)

def persistir_conteudo_conteiner_catalogo(
    conexao: Connection,
    conteudo: ConteudoConteinerCatalogoDTO,
) -> int:
    """
    Persiste um conteúdo associado a um contêiner.

    Utiliza a identidade composta por:
    - ID interno do contêiner;
    - fonte;
    - identificador externo do conteúdo;
    - tipo do conteúdo.

    Preserva informações opcionais existentes quando
    o DTO não fornece novos valores.

    Retorna o identificador interno do conteúdo.

    A conexão e a transação são controladas pelo chamador.
    """

    return inserir_ou_atualizar_conteudo_conteiner_catalogo(
        conexao,
        conteiner_catalogo_id=conteudo.conteiner_catalogo_id,
        fonte=conteudo.fonte,
        id_externo_conteudo=conteudo.id_externo_conteudo,
        nome_conteudo=conteudo.nome_conteudo,
        tipo_conteudo=conteudo.tipo_conteudo,
        raridade=conteudo.raridade,
        indice_pintura=conteudo.indice_pintura,
        nome_fase=conteudo.nome_fase,
        url_imagem=conteudo.url_imagem,
    )