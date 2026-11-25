from unittest.mock import Mock, patch

import pytest

from skinexa.dto.catalogo.colecoes import (
    ColecaoCatalogoDTO,
)

from skinexa.services.catalogo.colecoes import (
    persistir_colecao_catalogo,
)

def criar_colecao_catalogo_dto(
    *,
    fonte: str = "csgo_api",
    id_externo: str = "collection-set-fruits-veggies",
    nome: str = "Fruits And Veggies Sticker Collection",
    tipo_colecao: str | None = None,
    url_imagem: str | None = None,
) -> ColecaoCatalogoDTO:
    """Cria uma coleção simulada para os testes."""

    return ColecaoCatalogoDTO(
        fonte=fonte,
        id_externo=id_externo,
        nome=nome,
        tipo_colecao=tipo_colecao,
        url_imagem=url_imagem,
    )

@patch(
    "skinexa.services.catalogo.colecoes."
    "inserir_ou_atualizar_colecao_catalogo"
)

def test_persistir_colecao_catalogo(
    mock_inserir,
):
    """Persiste uma coleção e retorna seu ID interno."""

    conexao = Mock()
    colecao = criar_colecao_catalogo_dto()

    mock_inserir.return_value = 10

    resultado = persistir_colecao_catalogo(
        conexao,
        colecao,
    )

    assert resultado == 10

    mock_inserir.assert_called_once_with(
        conexao,
        fonte="csgo_api",
        id_externo="collection-set-fruits-veggies",
        nome="Fruits And Veggies Sticker Collection",
        tipo_colecao=None,
        url_imagem=None,
    )

@patch(
    "skinexa.services.catalogo.colecoes."
    "inserir_ou_atualizar_colecao_catalogo"
)

def test_persistir_colecao_catalogo_com_opcionais(
    mock_inserir,
):
    """Encaminha corretamente os campos opcionais."""

    conexao = Mock()

    colecao = criar_colecao_catalogo_dto(
        tipo_colecao="adesivo",
        url_imagem="https://exemplo.com/colecao.png",
    )

    mock_inserir.return_value = 20

    resultado = persistir_colecao_catalogo(
        conexao,
        colecao,
    )

    assert resultado == 20

    mock_inserir.assert_called_once_with(
        conexao,
        fonte="csgo_api",
        id_externo="collection-set-fruits-veggies",
        nome="Fruits And Veggies Sticker Collection",
        tipo_colecao="adesivo",
        url_imagem="https://exemplo.com/colecao.png",
    )

@patch(
    "skinexa.services.catalogo.colecoes."
    "inserir_ou_atualizar_colecao_catalogo"
)

def test_persistir_colecao_retorna_id_existente(
    mock_inserir,
):
    """Preserva o ID retornado quando a coleção já existe."""

    conexao = Mock()
    colecao = criar_colecao_catalogo_dto()

    mock_inserir.return_value = 10

    primeiro_id = persistir_colecao_catalogo(
        conexao,
        colecao,
    )

    segundo_id = persistir_colecao_catalogo(
        conexao,
        colecao,
    )

    assert primeiro_id == segundo_id == 10
    assert mock_inserir.call_count == 2

@patch(
    "skinexa.services.catalogo.colecoes."
    "inserir_ou_atualizar_colecao_catalogo"
)

def test_persistir_colecao_propaga_erro_query(
    mock_inserir,
):
    """Propaga falhas de persistência para o chamador."""

    conexao = Mock()
    colecao = criar_colecao_catalogo_dto()

    mock_inserir.side_effect = RuntimeError(
        "Falha ao persistir coleção."
    )

    with pytest.raises(
        RuntimeError,
        match="Falha ao persistir coleção",
    ):
        persistir_colecao_catalogo(
            conexao,
            colecao,
        )

    mock_inserir.assert_called_once()

@patch(
    "skinexa.services.catalogo.colecoes."
    "inserir_ou_atualizar_colecao_catalogo"
)

def test_persistir_colecao_preserva_dto(
    mock_inserir,
):
    """Não modifica os dados da coleção recebida."""

    conexao = Mock()
    colecao = criar_colecao_catalogo_dto()

    mock_inserir.return_value = 10

    estado_original = (
        colecao.fonte,
        colecao.id_externo,
        colecao.nome,
        colecao.tipo_colecao,
        colecao.url_imagem,
    )

    persistir_colecao_catalogo(
        conexao,
        colecao,
    )

    assert estado_original == (
        colecao.fonte,
        colecao.id_externo,
        colecao.nome,
        colecao.tipo_colecao,
        colecao.url_imagem,
    )