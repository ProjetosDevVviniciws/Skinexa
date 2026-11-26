from unittest.mock import Mock, patch

import pytest

from skinexa.dto.catalogo.conteineres import (
    ConteinerCatalogoDTO,
)

from skinexa.services.catalogo.conteineres import (
    persistir_conteiner_catalogo,
)

def criar_conteiner_catalogo_dto(
    *,
    fonte: str = "csgo_api",
    id_externo: str = "crate-4001",
    nome: str = "CS:GO Weapon Case",
    item_catalogo_id: int | None = None,
    tipo_conteiner: str | None = None,
    url_imagem: str | None = None,
) -> ConteinerCatalogoDTO:
    """Cria um contêiner simulado para os testes."""

    return ConteinerCatalogoDTO(
        fonte=fonte,
        id_externo=id_externo,
        nome=nome,
        item_catalogo_id=item_catalogo_id,
        tipo_conteiner=tipo_conteiner,
        url_imagem=url_imagem,
    )

@patch(
    "skinexa.services.catalogo.conteineres."
    "inserir_ou_atualizar_conteiner_catalogo"
)

def test_persistir_conteiner_catalogo(
    mock_inserir,
):
    """Persiste um contêiner e retorna seu ID interno."""

    conexao = Mock()
    conteiner = criar_conteiner_catalogo_dto()

    mock_inserir.return_value = 10

    resultado = persistir_conteiner_catalogo(
        conexao,
        conteiner,
    )

    assert resultado == 10

    mock_inserir.assert_called_once_with(
        conexao,
        fonte="csgo_api",
        id_externo="crate-4001",
        nome="CS:GO Weapon Case",
        item_catalogo_id=None,
        tipo_conteiner=None,
        url_imagem=None,
    )

@patch(
    "skinexa.services.catalogo.conteineres."
    "inserir_ou_atualizar_conteiner_catalogo"
)

def test_persistir_conteiner_com_opcionais(
    mock_inserir,
):
    """Encaminha os campos opcionais corretamente."""

    conexao = Mock()

    conteiner = criar_conteiner_catalogo_dto(
        item_catalogo_id=100,
        tipo_conteiner="Case",
        url_imagem="https://exemplo.com/caixa.png",
    )

    mock_inserir.return_value = 20

    resultado = persistir_conteiner_catalogo(
        conexao,
        conteiner,
    )

    assert resultado == 20

    mock_inserir.assert_called_once_with(
        conexao,
        fonte="csgo_api",
        id_externo="crate-4001",
        nome="CS:GO Weapon Case",
        item_catalogo_id=100,
        tipo_conteiner="Case",
        url_imagem="https://exemplo.com/caixa.png",
    )

@patch(
    "skinexa.services.catalogo.conteineres."
    "inserir_ou_atualizar_conteiner_catalogo"
)

def test_persistir_conteiner_retorna_id_existente(
    mock_inserir,
):
    """Repassa o ID retornado pela query em chamadas repetidas."""

    conexao = Mock()
    conteiner = criar_conteiner_catalogo_dto()

    mock_inserir.return_value = 10

    primeiro_id = persistir_conteiner_catalogo(
        conexao,
        conteiner,
    )

    segundo_id = persistir_conteiner_catalogo(
        conexao,
        conteiner,
    )

    assert primeiro_id == segundo_id == 10
    assert mock_inserir.call_count == 2

@patch(
    "skinexa.services.catalogo.conteineres."
    "inserir_ou_atualizar_conteiner_catalogo"
)

def test_persistir_conteiner_sem_vinculo_comercial(
    mock_inserir,
):
    """Não inventa vínculo comercial para o contêiner."""

    conexao = Mock()

    conteiner = criar_conteiner_catalogo_dto(
        item_catalogo_id=None,
    )

    mock_inserir.return_value = 30

    resultado = persistir_conteiner_catalogo(
        conexao,
        conteiner,
    )

    assert resultado == 30

    assert (
        mock_inserir.call_args.kwargs["item_catalogo_id"]
        is None
    )

@patch(
    "skinexa.services.catalogo.conteineres."
    "inserir_ou_atualizar_conteiner_catalogo"
)

def test_persistir_conteiner_propaga_erro_query(
    mock_inserir,
):
    """Propaga falhas da query para o chamador."""

    conexao = Mock()
    conteiner = criar_conteiner_catalogo_dto()

    mock_inserir.side_effect = RuntimeError(
        "Falha ao persistir contêiner."
    )

    with pytest.raises(
        RuntimeError,
        match="Falha ao persistir contêiner",
    ):
        persistir_conteiner_catalogo(
            conexao,
            conteiner,
        )

    mock_inserir.assert_called_once()

@patch(
    "skinexa.services.catalogo.conteineres."
    "inserir_ou_atualizar_conteiner_catalogo"
)

def test_persistir_conteiner_preserva_dto(
    mock_inserir,
):
    """Não modifica o DTO recebido."""

    conexao = Mock()
    conteiner = criar_conteiner_catalogo_dto()

    mock_inserir.return_value = 10

    estado_original = (
        conteiner.fonte,
        conteiner.id_externo,
        conteiner.nome,
        conteiner.item_catalogo_id,
        conteiner.tipo_conteiner,
        conteiner.url_imagem,
    )

    persistir_conteiner_catalogo(
        conexao,
        conteiner,
    )

    assert estado_original == (
        conteiner.fonte,
        conteiner.id_externo,
        conteiner.nome,
        conteiner.item_catalogo_id,
        conteiner.tipo_conteiner,
        conteiner.url_imagem,
    )

@patch(
    "skinexa.services.catalogo.conteineres."
    "inserir_ou_atualizar_conteiner_catalogo"
)

def test_persistir_conteiner_nao_gerencia_transacao(
    mock_inserir,
):
    """Não abre, confirma ou reverte transações."""

    conexao = Mock()
    conteiner = criar_conteiner_catalogo_dto()

    mock_inserir.return_value = 10

    persistir_conteiner_catalogo(
        conexao,
        conteiner,
    )

    conexao.begin.assert_not_called()
    conexao.commit.assert_not_called()
    conexao.rollback.assert_not_called()

    mock_inserir.assert_called_once()