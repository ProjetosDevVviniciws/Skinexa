"""Serviços de relacionamentos entre itens e coleções do catálogo."""

from sqlalchemy.engine import Connection

from skinexa.database.queries.itens_colecoes_catalogo import (
    inserir_ou_preservar_relacao_item_colecao,
)

from skinexa.dto.catalogo.colecoes import (
    RelacaoItemColecaoDTO,
)

def persistir_relacao_item_colecao(
    conexao: Connection,
    relacao: RelacaoItemColecaoDTO,
) -> None:
    """
    Persiste uma associação entre um item e uma coleção.

    Utiliza os identificadores internos previamente
    resolvidos pela camada de serviço.

    Quando a associação já existe, preserva seus dados
    e não modifica a fonte original da relação.

    A conexão e a transação são controladas pelo chamador.
    """

    inserir_ou_preservar_relacao_item_colecao(
        conexao,
        item_catalogo_id=relacao.item_catalogo_id,
        colecao_catalogo_id=relacao.colecao_catalogo_id,
        fonte_relacao=relacao.fonte_relacao,
    )