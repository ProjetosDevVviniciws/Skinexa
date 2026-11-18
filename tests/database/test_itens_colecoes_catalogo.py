from unittest.mock import Mock

import pytest

from skinexa.database.queries.itens_colecoes_catalogo import (
    contar_relacoes_itens_colecoes_catalogo,
    inserir_ou_preservar_relacao_item_colecao,
    listar_colecoes_por_item_catalogo,
)

def criar_registro_colecao_vinculada(
    *,
    colecao_id: int = 10,
    nome: str = "The Huntsman Collection",
) -> Mock:
    """Cria um registro simulado de coleção vinculada."""

    registro = Mock()

    registro._mapping = {
        "id": colecao_id,
        "fonte": "csgo_api",
        "id_externo": "collection-set-community-2",
        "nome": nome,
        "tipo_colecao": "skin",
        "url_imagem": None,
        "fonte_relacao": "csgo_api",
        "relacao_criada_em": None,
    }

    return registro

def test_inserir_relacao_item_colecao():
    """Testa a inserção de uma associação válida."""

    conexao = Mock()

    resultado = inserir_ou_preservar_relacao_item_colecao(
        conexao,
        item_catalogo_id=100,
        colecao_catalogo_id=10,
        fonte_relacao="csgo_api",
    )

    assert resultado is None

    conexao.execute.assert_called_once()

def test_inserir_relacao_envia_parametros_corretos():
    """Verifica os parâmetros enviados ao banco."""

    conexao = Mock()

    inserir_ou_preservar_relacao_item_colecao(
        conexao,
        item_catalogo_id=100,
        colecao_catalogo_id=10,
        fonte_relacao="csgo_api",
    )

    parametros = conexao.execute.call_args.args[1]

    assert parametros == {
        "item_catalogo_id": 100,
        "colecao_catalogo_id": 10,
        "fonte_relacao": "csgo_api",
    }

def test_inserir_relacao_normaliza_fonte():
    """Remove espaços da fonte antes da persistência."""

    conexao = Mock()

    inserir_ou_preservar_relacao_item_colecao(
        conexao,
        item_catalogo_id=100,
        colecao_catalogo_id=10,
        fonte_relacao="  csgo_api  ",
    )

    parametros = conexao.execute.call_args.args[1]

    assert parametros["fonte_relacao"] == "csgo_api"

@pytest.mark.parametrize(
    "item_catalogo_id",
    [0, -1, -100],
)

def test_inserir_relacao_rejeita_item_id_invalido(
    item_catalogo_id,
):
    """Rejeita identificadores inválidos de itens."""

    conexao = Mock()

    with pytest.raises(
        ValueError,
        match="ID do item deve ser maior que zero",
    ):
        inserir_ou_preservar_relacao_item_colecao(
            conexao,
            item_catalogo_id=item_catalogo_id,
            colecao_catalogo_id=10,
            fonte_relacao="csgo_api",
        )

    conexao.execute.assert_not_called()

@pytest.mark.parametrize(
    "colecao_catalogo_id",
    [0, -1, -100],
)

def test_inserir_relacao_rejeita_colecao_id_invalido(
    colecao_catalogo_id,
):
    """Rejeita identificadores inválidos de coleções."""

    conexao = Mock()

    with pytest.raises(
        ValueError,
        match="ID da coleção deve ser maior que zero",
    ):
        inserir_ou_preservar_relacao_item_colecao(
            conexao,
            item_catalogo_id=100,
            colecao_catalogo_id=colecao_catalogo_id,
            fonte_relacao="csgo_api",
        )

    conexao.execute.assert_not_called()

def test_inserir_relacao_rejeita_fonte_vazia():
    """Não permite relacionamentos sem fonte válida."""

    conexao = Mock()

    with pytest.raises(
        ValueError,
        match="fonte da relação não pode ser vazia",
    ):
        inserir_ou_preservar_relacao_item_colecao(
            conexao,
            item_catalogo_id=100,
            colecao_catalogo_id=10,
            fonte_relacao="   ",
        )

    conexao.execute.assert_not_called()

def test_inserir_relacao_preserva_associacao_existente():
    """Verifica a estratégia de preservação da relação."""

    conexao = Mock()

    inserir_ou_preservar_relacao_item_colecao(
        conexao,
        item_catalogo_id=100,
        colecao_catalogo_id=10,
        fonte_relacao="csgo_api",
    )

    consulta = str(
        conexao.execute.call_args.args[0]
    )

    assert "ON DUPLICATE KEY UPDATE" in consulta
    assert "fonte_relacao = fonte_relacao" in consulta

    conexao.execute.assert_called_once()

def test_listar_colecoes_por_item():
    """Testa a listagem das coleções de um item."""

    conexao = Mock()

    registro_1 = criar_registro_colecao_vinculada(
        colecao_id=10,
        nome="The Huntsman Collection",
    )

    registro_2 = criar_registro_colecao_vinculada(
        colecao_id=20,
        nome="The Phoenix Collection",
    )

    conexao.execute.return_value = [
        registro_1,
        registro_2,
    ]

    resultado = listar_colecoes_por_item_catalogo(
        conexao,
        item_catalogo_id=100,
    )

    assert resultado == [
        registro_1._mapping,
        registro_2._mapping,
    ]

    conexao.execute.assert_called_once()

def test_listar_colecoes_por_item_sem_resultados():
    """Retorna lista vazia para item sem coleções."""

    conexao = Mock()
    conexao.execute.return_value = []

    resultado = listar_colecoes_por_item_catalogo(
        conexao,
        item_catalogo_id=100,
    )

    assert resultado == []

    conexao.execute.assert_called_once()

def test_listar_colecoes_por_item_envia_parametro():
    """Verifica o ID utilizado na consulta."""

    conexao = Mock()
    conexao.execute.return_value = []

    listar_colecoes_por_item_catalogo(
        conexao,
        item_catalogo_id=100,
    )

    parametros = conexao.execute.call_args.args[1]

    assert parametros == {
        "item_catalogo_id": 100,
    }

def test_listar_colecoes_por_item_utiliza_join():
    """Confirma a associação com os dados da coleção."""

    conexao = Mock()
    conexao.execute.return_value = []

    listar_colecoes_por_item_catalogo(
        conexao,
        item_catalogo_id=100,
    )

    consulta = str(
        conexao.execute.call_args.args[0]
    )

    assert "INNER JOIN colecoes_catalogo" in consulta
    assert "c.id = ic.colecao_catalogo_id" in consulta
    assert "ic.item_catalogo_id = :item_catalogo_id" in consulta

@pytest.mark.parametrize(
    "item_catalogo_id",
    [0, -1],
)

def test_listar_colecoes_por_item_com_id_invalido(
    item_catalogo_id,
):
    """Evita consultar o banco com ID inválido."""

    conexao = Mock()

    resultado = listar_colecoes_por_item_catalogo(
        conexao,
        item_catalogo_id=item_catalogo_id,
    )

    assert resultado == []

    conexao.execute.assert_not_called()

def test_contar_relacoes_itens_colecoes_catalogo():
    """Testa a contagem total de relacionamentos."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.scalar_one.return_value = 16865

    conexao.execute.return_value = resultado_execute

    resultado = contar_relacoes_itens_colecoes_catalogo(
        conexao,
    )

    assert resultado == 16865

    conexao.execute.assert_called_once()

def test_contar_relacoes_itens_colecoes_catalogo_vazio():
    """Testa a contagem sem relacionamentos."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.scalar_one.return_value = 0

    conexao.execute.return_value = resultado_execute

    resultado = contar_relacoes_itens_colecoes_catalogo(
        conexao,
    )

    assert resultado == 0

    conexao.execute.assert_called_once()