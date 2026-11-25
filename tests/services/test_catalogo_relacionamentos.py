from unittest.mock import Mock, patch

import pytest

from skinexa.dto.catalogo.colecoes import (
    RelacaoItemColecaoDTO,
)

from skinexa.services.catalogo.relacionamentos import (
    persistir_relacao_item_colecao,
)

def criar_relacao_item_colecao_dto(
    *,
    item_catalogo_id: int = 100,
    colecao_catalogo_id: int = 10,
    fonte_relacao: str = "csgo_api",
) -> RelacaoItemColecaoDTO:
    """Cria uma relação simulada para os testes."""

    return RelacaoItemColecaoDTO(
        item_catalogo_id=item_catalogo_id,
        colecao_catalogo_id=colecao_catalogo_id,
        fonte_relacao=fonte_relacao,
    )

@patch(
    "skinexa.services.catalogo.relacionamentos."
    "inserir_ou_preservar_relacao_item_colecao"
)

def test_persistir_relacao_item_colecao(
    mock_inserir,
):
    """Encaminha corretamente os dados da associação."""

    conexao = Mock()
    relacao = criar_relacao_item_colecao_dto()

    resultado = persistir_relacao_item_colecao(
        conexao,
        relacao,
    )

    assert resultado is None

    mock_inserir.assert_called_once_with(
        conexao,
        item_catalogo_id=100,
        colecao_catalogo_id=10,
        fonte_relacao="csgo_api",
    )

@patch(
    "skinexa.services.catalogo.relacionamentos."
    "inserir_ou_preservar_relacao_item_colecao"
)

def test_persistir_relacao_com_ids_diferentes(
    mock_inserir,
):
    """Encaminha os identificadores específicos da relação."""

    conexao = Mock()

    relacao = criar_relacao_item_colecao_dto(
        item_catalogo_id=250,
        colecao_catalogo_id=35,
    )

    persistir_relacao_item_colecao(
        conexao,
        relacao,
    )

    mock_inserir.assert_called_once_with(
        conexao,
        item_catalogo_id=250,
        colecao_catalogo_id=35,
        fonte_relacao="csgo_api",
    )

@patch(
    "skinexa.services.catalogo.relacionamentos."
    "inserir_ou_preservar_relacao_item_colecao"
)

def test_persistir_relacao_com_fonte_diferente(
    mock_inserir,
):
    """Preserva a fonte informada no DTO."""

    conexao = Mock()

    relacao = criar_relacao_item_colecao_dto(
        fonte_relacao="importacao_legada",
    )

    persistir_relacao_item_colecao(
        conexao,
        relacao,
    )

    mock_inserir.assert_called_once_with(
        conexao,
        item_catalogo_id=100,
        colecao_catalogo_id=10,
        fonte_relacao="importacao_legada",
    )

@patch(
    "skinexa.services.catalogo.relacionamentos."
    "inserir_ou_preservar_relacao_item_colecao"
)

def test_persistir_relacao_repetida(
    mock_inserir,
):
    """Permite repetir a operação sem modificar seus argumentos."""

    conexao = Mock()
    relacao = criar_relacao_item_colecao_dto()

    primeiro_resultado = persistir_relacao_item_colecao(
        conexao,
        relacao,
    )

    segundo_resultado = persistir_relacao_item_colecao(
        conexao,
        relacao,
    )

    assert primeiro_resultado is None
    assert segundo_resultado is None

    assert mock_inserir.call_count == 2

    for chamada in mock_inserir.call_args_list:
        assert chamada.args == (conexao,)
        assert chamada.kwargs == {
            "item_catalogo_id": 100,
            "colecao_catalogo_id": 10,
            "fonte_relacao": "csgo_api",
        }

@patch(
    "skinexa.services.catalogo.relacionamentos."
    "inserir_ou_preservar_relacao_item_colecao"
)

def test_persistir_relacao_propaga_erro_query(
    mock_inserir,
):
    """Propaga falhas da query para o chamador."""

    conexao = Mock()
    relacao = criar_relacao_item_colecao_dto()

    mock_inserir.side_effect = RuntimeError(
        "Falha ao persistir relacionamento."
    )

    with pytest.raises(
        RuntimeError,
        match="Falha ao persistir relacionamento",
    ):
        persistir_relacao_item_colecao(
            conexao,
            relacao,
        )

    mock_inserir.assert_called_once()

@patch(
    "skinexa.services.catalogo.relacionamentos."
    "inserir_ou_preservar_relacao_item_colecao"
)

def test_persistir_relacao_preserva_dto(
    mock_inserir,
):
    """Não modifica o DTO recebido."""

    conexao = Mock()
    relacao = criar_relacao_item_colecao_dto()

    estado_original = (
        relacao.item_catalogo_id,
        relacao.colecao_catalogo_id,
        relacao.fonte_relacao,
    )

    persistir_relacao_item_colecao(
        conexao,
        relacao,
    )

    assert estado_original == (
        relacao.item_catalogo_id,
        relacao.colecao_catalogo_id,
        relacao.fonte_relacao,
    )

@patch(
    "skinexa.services.catalogo.relacionamentos."
    "inserir_ou_preservar_relacao_item_colecao"
)

def test_persistir_relacao_nao_gerencia_transacao(
    mock_inserir,
):
    """Não abre, confirma ou reverte transações."""

    conexao = Mock()
    relacao = criar_relacao_item_colecao_dto()

    persistir_relacao_item_colecao(
        conexao,
        relacao,
    )

    conexao.begin.assert_not_called()
    conexao.commit.assert_not_called()
    conexao.rollback.assert_not_called()

    mock_inserir.assert_called_once()