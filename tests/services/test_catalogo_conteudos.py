from unittest.mock import Mock, patch

import pytest

from skinexa.dto.catalogo.conteineres import (
    ConteudoConteinerCatalogoDTO,
)

from skinexa.services.catalogo.conteudos import (
    persistir_conteudo_conteiner_catalogo,
)

def criar_conteudo_conteiner_catalogo_dto(
    *,
    conteiner_catalogo_id: int = 10,
    fonte: str = "csgo_api",
    id_externo_conteudo: str = "skin-2ca8cb95f31e",
    nome_conteudo: str = "MP7 | Skulls",
    tipo_conteudo: str = "contains",
    raridade: str | None = None,
    indice_pintura: int | None = None,
    nome_fase: str | None = None,
    url_imagem: str | None = None,
) -> ConteudoConteinerCatalogoDTO:
    """Cria um conteúdo simulado para os testes."""

    return ConteudoConteinerCatalogoDTO(
        conteiner_catalogo_id=conteiner_catalogo_id,
        fonte=fonte,
        id_externo_conteudo=id_externo_conteudo,
        nome_conteudo=nome_conteudo,
        tipo_conteudo=tipo_conteudo,
        raridade=raridade,
        indice_pintura=indice_pintura,
        nome_fase=nome_fase,
        url_imagem=url_imagem,
    )

@patch(
    "skinexa.services.catalogo.conteudos."
    "inserir_ou_atualizar_conteudo_conteiner_catalogo"
)

def test_persistir_conteudo_conteiner_catalogo(
    mock_inserir,
):
    """Persiste um conteúdo e retorna seu ID interno."""

    conexao = Mock()
    conteudo = criar_conteudo_conteiner_catalogo_dto()

    mock_inserir.return_value = 25

    resultado = persistir_conteudo_conteiner_catalogo(
        conexao,
        conteudo,
    )

    assert resultado == 25

    mock_inserir.assert_called_once_with(
        conexao,
        conteiner_catalogo_id=10,
        fonte="csgo_api",
        id_externo_conteudo="skin-2ca8cb95f31e",
        nome_conteudo="MP7 | Skulls",
        tipo_conteudo="contains",
        raridade=None,
        indice_pintura=None,
        nome_fase=None,
        url_imagem=None,
    )

@patch(
    "skinexa.services.catalogo.conteudos."
    "inserir_ou_atualizar_conteudo_conteiner_catalogo"
)

def test_persistir_conteudo_com_opcionais(
    mock_inserir,
):
    """Encaminha corretamente os metadados opcionais."""

    conexao = Mock()

    conteudo = criar_conteudo_conteiner_catalogo_dto(
        raridade="Mil-Spec Grade",
        indice_pintura=11,
        nome_fase="Phase 1",
        url_imagem="https://exemplo.com/mp7.png",
    )

    mock_inserir.return_value = 35

    resultado = persistir_conteudo_conteiner_catalogo(
        conexao,
        conteudo,
    )

    assert resultado == 35

    mock_inserir.assert_called_once_with(
        conexao,
        conteiner_catalogo_id=10,
        fonte="csgo_api",
        id_externo_conteudo="skin-2ca8cb95f31e",
        nome_conteudo="MP7 | Skulls",
        tipo_conteudo="contains",
        raridade="Mil-Spec Grade",
        indice_pintura=11,
        nome_fase="Phase 1",
        url_imagem="https://exemplo.com/mp7.png",
    )

@patch(
    "skinexa.services.catalogo.conteudos."
    "inserir_ou_atualizar_conteudo_conteiner_catalogo"
)

def test_persistir_conteudo_contains_rare(
    mock_inserir,
):
    """Persiste conteúdos classificados como contains_rare."""

    conexao = Mock()

    conteudo = criar_conteudo_conteiner_catalogo_dto(
        id_externo_conteudo="skin-vanilla-weapon_bayonet",
        nome_conteudo="Bayonet",
        tipo_conteudo="contains_rare",
    )

    mock_inserir.return_value = 45

    resultado = persistir_conteudo_conteiner_catalogo(
        conexao,
        conteudo,
    )

    assert resultado == 45

    mock_inserir.assert_called_once_with(
        conexao,
        conteiner_catalogo_id=10,
        fonte="csgo_api",
        id_externo_conteudo="skin-vanilla-weapon_bayonet",
        nome_conteudo="Bayonet",
        tipo_conteudo="contains_rare",
        raridade=None,
        indice_pintura=None,
        nome_fase=None,
        url_imagem=None,
    )

@patch(
    "skinexa.services.catalogo.conteudos."
    "inserir_ou_atualizar_conteudo_conteiner_catalogo"
)

def test_persistir_conteudo_retorna_id_existente(
    mock_inserir,
):
    """Repassa o ID retornado pela query em chamadas repetidas."""

    conexao = Mock()
    conteudo = criar_conteudo_conteiner_catalogo_dto()

    mock_inserir.return_value = 25

    primeiro_id = persistir_conteudo_conteiner_catalogo(
        conexao,
        conteudo,
    )

    segundo_id = persistir_conteudo_conteiner_catalogo(
        conexao,
        conteudo,
    )

    assert primeiro_id == segundo_id == 25
    assert mock_inserir.call_count == 2

@patch(
    "skinexa.services.catalogo.conteudos."
    "inserir_ou_atualizar_conteudo_conteiner_catalogo"
)

def test_persistir_conteudo_propaga_erro_query(
    mock_inserir,
):
    """Propaga falhas da query para o chamador."""

    conexao = Mock()
    conteudo = criar_conteudo_conteiner_catalogo_dto()

    mock_inserir.side_effect = RuntimeError(
        "Falha ao persistir conteúdo."
    )

    with pytest.raises(
        RuntimeError,
        match="Falha ao persistir conteúdo",
    ):
        persistir_conteudo_conteiner_catalogo(
            conexao,
            conteudo,
        )

    mock_inserir.assert_called_once()

@patch(
    "skinexa.services.catalogo.conteudos."
    "inserir_ou_atualizar_conteudo_conteiner_catalogo"
)

def test_persistir_conteudo_preserva_dto(
    mock_inserir,
):
    """Não modifica o DTO recebido."""

    conexao = Mock()
    conteudo = criar_conteudo_conteiner_catalogo_dto()

    mock_inserir.return_value = 25

    estado_original = (
        conteudo.conteiner_catalogo_id,
        conteudo.fonte,
        conteudo.id_externo_conteudo,
        conteudo.nome_conteudo,
        conteudo.tipo_conteudo,
        conteudo.raridade,
        conteudo.indice_pintura,
        conteudo.nome_fase,
        conteudo.url_imagem,
    )

    persistir_conteudo_conteiner_catalogo(
        conexao,
        conteudo,
    )

    assert estado_original == (
        conteudo.conteiner_catalogo_id,
        conteudo.fonte,
        conteudo.id_externo_conteudo,
        conteudo.nome_conteudo,
        conteudo.tipo_conteudo,
        conteudo.raridade,
        conteudo.indice_pintura,
        conteudo.nome_fase,
        conteudo.url_imagem,
    )

@patch(
    "skinexa.services.catalogo.conteudos."
    "inserir_ou_atualizar_conteudo_conteiner_catalogo"
)

def test_persistir_conteudo_nao_gerencia_transacao(
    mock_inserir,
):
    """Não abre, confirma ou reverte transações."""

    conexao = Mock()
    conteudo = criar_conteudo_conteiner_catalogo_dto()

    mock_inserir.return_value = 25

    persistir_conteudo_conteiner_catalogo(
        conexao,
        conteudo,
    )

    conexao.begin.assert_not_called()
    conexao.commit.assert_not_called()
    conexao.rollback.assert_not_called()

    mock_inserir.assert_called_once()