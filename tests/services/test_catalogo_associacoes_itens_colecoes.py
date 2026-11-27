from unittest.mock import Mock, call, patch

import pytest

from skinexa.dto.catalogo.colecoes import (
    ColecaoCatalogoDTO,
    RelacaoItemColecaoDTO,
)

from skinexa.services.catalogo.associacoes_itens_colecoes import (
    associar_itens_colecao_catalogo,
)

MODULO = (
    "skinexa.services.catalogo."
    "associacoes_itens_colecoes"
)

@pytest.fixture
def colecao():
    """Cria uma coleção simulada da CSGO-API."""

    return ColecaoCatalogoDTO(
        fonte="csgo_api",
        id_externo="collection-test",
        nome="Test Collection",
    )

@pytest.fixture
def mocks_persistencia():
    """Simula a consulta e os services de persistência."""

    with (
        patch(
            f"{MODULO}.obter_itens_catalogo_ids_por_skin_ids"
        ) as mock_obter_itens,
        patch(
            f"{MODULO}.persistir_colecao_catalogo"
        ) as mock_persistir_colecao,
        patch(
            f"{MODULO}.persistir_relacao_item_colecao"
        ) as mock_persistir_relacao,
    ):
        mock_obter_itens.return_value = {}
        mock_persistir_colecao.return_value = 10

        yield (
            mock_obter_itens,
            mock_persistir_colecao,
            mock_persistir_relacao,
        )

def test_associar_itens_colecao_catalogo(
    colecao,
    mocks_persistencia,
):
    """Associa todas as variantes comerciais de uma skin."""

    conexao = Mock()

    (
        mock_obter_itens,
        mock_persistir_colecao,
        mock_persistir_relacao,
    ) = mocks_persistencia

    mock_obter_itens.return_value = {
        "skin-ak47": [100, 101, 102],
    }

    resultado = associar_itens_colecao_catalogo(
        conexao,
        colecao,
        {"skin-ak47"},
    )

    assert resultado == (10, 3, 0)

    mock_obter_itens.assert_called_once_with(
        conexao,
        {"skin-ak47"},
    )

    mock_persistir_colecao.assert_called_once_with(
        conexao,
        colecao,
    )

    assert mock_persistir_relacao.call_args_list == [
        call(
            conexao,
            RelacaoItemColecaoDTO(
                item_catalogo_id=100,
                colecao_catalogo_id=10,
                fonte_relacao="csgo_api",
            ),
        ),
        call(
            conexao,
            RelacaoItemColecaoDTO(
                item_catalogo_id=101,
                colecao_catalogo_id=10,
                fonte_relacao="csgo_api",
            ),
        ),
        call(
            conexao,
            RelacaoItemColecaoDTO(
                item_catalogo_id=102,
                colecao_catalogo_id=10,
                fonte_relacao="csgo_api",
            ),
        ),
    ]

def test_associar_multiplas_skins_colecao(
    colecao,
    mocks_persistencia,
):
    """Associa itens de diferentes skins à mesma coleção."""

    conexao = Mock()

    (
        mock_obter_itens,
        _,
        mock_persistir_relacao,
    ) = mocks_persistencia

    mock_obter_itens.return_value = {
        "skin-ak47": [100, 101],
        "skin-awp": [200, 201],
    }

    resultado = associar_itens_colecao_catalogo(
        conexao,
        colecao,
        {"skin-ak47", "skin-awp"},
    )

    assert resultado == (10, 4, 0)
    assert mock_persistir_relacao.call_count == 4

    ids_associados = {
        chamada.args[1].item_catalogo_id
        for chamada in mock_persistir_relacao.call_args_list
    }

    assert ids_associados == {
        100, 101, 200, 201,
    }

def test_associar_skin_sem_correspondencia(
    colecao,
    mocks_persistencia,
):
    """Contabiliza skins que não possuem itens comerciais."""

    conexao = Mock()

    (
        mock_obter_itens,
        mock_persistir_colecao,
        mock_persistir_relacao,
    ) = mocks_persistencia

    mock_obter_itens.return_value = {
        "skin-ak47": [100, 101],
    }

    resultado = associar_itens_colecao_catalogo(
        conexao,
        colecao,
        {"skin-ak47", "skin-inexistente"},
    )

    assert resultado == (10, 2, 1)

    mock_persistir_colecao.assert_called_once()
    assert mock_persistir_relacao.call_count == 2

def test_associar_todas_skins_sem_correspondencia(
    colecao,
    mocks_persistencia,
):
    """Persiste a coleção mesmo sem itens correspondentes."""

    conexao = Mock()

    (
        mock_obter_itens,
        mock_persistir_colecao,
        mock_persistir_relacao,
    ) = mocks_persistencia

    mock_obter_itens.return_value = {}

    resultado = associar_itens_colecao_catalogo(
        conexao,
        colecao,
        {"skin-inexistente"},
    )

    assert resultado == (10, 0, 1)

    mock_persistir_colecao.assert_called_once()
    mock_persistir_relacao.assert_not_called()

def test_associar_remove_ids_comerciais_duplicados(
    colecao,
    mocks_persistencia,
):
    """Evita processar o mesmo item duas vezes na coleção."""

    conexao = Mock()

    (
        mock_obter_itens,
        _,
        mock_persistir_relacao,
    ) = mocks_persistencia

    mock_obter_itens.return_value = {
        "skin-ak47": [100, 100, 101],
        "skin-awp": [101, 200],
    }

    resultado = associar_itens_colecao_catalogo(
        conexao,
        colecao,
        {"skin-ak47", "skin-awp"},
    )

    assert resultado == (10, 3, 0)

    ids_associados = [
        chamada.args[1].item_catalogo_id
        for chamada in mock_persistir_relacao.call_args_list
    ]

    assert ids_associados == [100, 101, 200]

def test_associar_normaliza_skin_ids(
    colecao,
    mocks_persistencia,
):
    """Remove espaços antes de consultar os identificadores."""

    conexao = Mock()

    (
        mock_obter_itens,
        _,
        _,
    ) = mocks_persistencia

    mock_obter_itens.return_value = {
        "skin-ak47": [100],
    }

    resultado = associar_itens_colecao_catalogo(
        conexao,
        colecao,
        {"  skin-ak47  ", "skin-ak47"},
    )

    assert resultado == (10, 1, 0)

    mock_obter_itens.assert_called_once_with(
        conexao,
        {"skin-ak47"},
    )

def test_associar_conjunto_vazio(
    colecao,
    mocks_persistencia,
):
    """Permite persistir uma coleção sem skins informadas."""

    conexao = Mock()

    (
        mock_obter_itens,
        mock_persistir_colecao,
        mock_persistir_relacao,
    ) = mocks_persistencia

    resultado = associar_itens_colecao_catalogo(
        conexao,
        colecao,
        set(),
    )

    assert resultado == (10, 0, 0)

    mock_obter_itens.assert_called_once_with(
        conexao,
        set(),
    )
    mock_persistir_colecao.assert_called_once()
    mock_persistir_relacao.assert_not_called()

@pytest.mark.parametrize(
    "skin_ids",
    [
        None,
        [],
        ("skin-ak47",),
        "skin-ak47",
    ],
)

def test_associar_rejeita_skin_ids_sem_set(
    colecao,
    mocks_persistencia,
    skin_ids,
):
    """Exige um conjunto de identificadores."""

    conexao = Mock()

    (
        mock_obter_itens,
        mock_persistir_colecao,
        mock_persistir_relacao,
    ) = mocks_persistencia

    with pytest.raises(
        ValueError,
        match="Os skin_ids devem ser fornecidos como um conjunto",
    ):
        associar_itens_colecao_catalogo(
            conexao,
            colecao,
            skin_ids,
        )

    mock_obter_itens.assert_not_called()
    mock_persistir_colecao.assert_not_called()
    mock_persistir_relacao.assert_not_called()

@pytest.mark.parametrize(
    "skin_id",
    [
        "",
        "   ",
        123,
        None,
    ],
)

def test_associar_rejeita_skin_id_invalido(
    colecao,
    mocks_persistencia,
    skin_id,
):
    """Rejeita identificadores vazios ou não textuais."""

    conexao = Mock()

    (
        mock_obter_itens,
        mock_persistir_colecao,
        mock_persistir_relacao,
    ) = mocks_persistencia

    with pytest.raises(ValueError):
        associar_itens_colecao_catalogo(
            conexao,
            colecao,
            {skin_id},
        )

    mock_obter_itens.assert_not_called()
    mock_persistir_colecao.assert_not_called()
    mock_persistir_relacao.assert_not_called()

def test_associar_rejeita_skin_id_nao_solicitado(
    colecao,
    mocks_persistencia,
):
    """Rejeita resultados de skins não solicitadas."""

    conexao = Mock()

    (
        mock_obter_itens,
        mock_persistir_colecao,
        mock_persistir_relacao,
    ) = mocks_persistencia

    mock_obter_itens.return_value = {
        "skin-outra": [100],
    }

    with pytest.raises(
        RuntimeError,
        match="skin_id não solicitado",
    ):
        associar_itens_colecao_catalogo(
            conexao,
            colecao,
            {"skin-ak47"},
        )

    mock_persistir_colecao.assert_not_called()
    mock_persistir_relacao.assert_not_called()

@pytest.mark.parametrize(
    "item_id",
    [
        0,
        -1,
        None,
        True,
        "100",
    ],
)

def test_associar_rejeita_item_comercial_invalido(
    colecao,
    mocks_persistencia,
    item_id,
):
    """Rejeita IDs comerciais inválidos antes das gravações."""

    conexao = Mock()

    (
        mock_obter_itens,
        mock_persistir_colecao,
        mock_persistir_relacao,
    ) = mocks_persistencia

    mock_obter_itens.return_value = {
        "skin-ak47": [item_id],
    }

    with pytest.raises(
        RuntimeError,
        match="IDs comerciais inválidos",
    ):
        associar_itens_colecao_catalogo(
            conexao,
            colecao,
            {"skin-ak47"},
        )

    mock_persistir_colecao.assert_not_called()
    mock_persistir_relacao.assert_not_called()

@pytest.mark.parametrize(
    "colecao_id",
    [
        0,
        -1,
        None,
    ],
)

def test_associar_rejeita_colecao_id_invalido(
    colecao,
    mocks_persistencia,
    colecao_id,
):
    """Não persiste relações com ID inválido de coleção."""

    conexao = Mock()

    (
        mock_obter_itens,
        mock_persistir_colecao,
        mock_persistir_relacao,
    ) = mocks_persistencia

    mock_obter_itens.return_value = {
        "skin-ak47": [100],
    }

    mock_persistir_colecao.return_value = colecao_id

    with pytest.raises(
        RuntimeError,
        match="O ID interno da coleção é inválido",
    ):
        associar_itens_colecao_catalogo(
            conexao,
            colecao,
            {"skin-ak47"},
        )

    mock_persistir_relacao.assert_not_called()

def test_associar_propaga_erro_consulta(
    colecao,
    mocks_persistencia,
):
    """Propaga falha da consulta sem iniciar persistência."""

    conexao = Mock()

    (
        mock_obter_itens,
        mock_persistir_colecao,
        mock_persistir_relacao,
    ) = mocks_persistencia

    mock_obter_itens.side_effect = RuntimeError(
        "Falha ao consultar itens."
    )

    with pytest.raises(
        RuntimeError,
        match="Falha ao consultar itens",
    ):
        associar_itens_colecao_catalogo(
            conexao,
            colecao,
            {"skin-ak47"},
        )

    mock_persistir_colecao.assert_not_called()
    mock_persistir_relacao.assert_not_called()

def test_associar_propaga_erro_persistencia(
    colecao,
    mocks_persistencia,
):
    """Propaga falhas ao registrar relacionamentos."""

    conexao = Mock()

    (
        mock_obter_itens,
        _,
        mock_persistir_relacao,
    ) = mocks_persistencia

    mock_obter_itens.return_value = {
        "skin-ak47": [100],
    }

    mock_persistir_relacao.side_effect = RuntimeError(
        "Falha ao persistir relação."
    )

    with pytest.raises(
        RuntimeError,
        match="Falha ao persistir relação",
    ):
        associar_itens_colecao_catalogo(
            conexao,
            colecao,
            {"skin-ak47"},
        )

def test_associar_nao_gerencia_transacao(
    colecao,
    mocks_persistencia,
):
    """Mantém o gerenciamento transacional com o chamador."""

    conexao = Mock()

    (
        mock_obter_itens,
        _,
        _,
    ) = mocks_persistencia

    mock_obter_itens.return_value = {
        "skin-ak47": [100],
    }

    associar_itens_colecao_catalogo(
        conexao,
        colecao,
        {"skin-ak47"},
    )

    conexao.begin.assert_not_called()
    conexao.commit.assert_not_called()
    conexao.rollback.assert_not_called()