import pytest

from unittest.mock import Mock

from skinexa.database.queries.variantes_itens_catalogo import (
    inserir_ou_atualizar_variante_catalogo_importacao,
)

from skinexa.dto.catalogo.variante import (
    VarianteImportacaoCatalogoDTO,
)

def test_importacao_variante_retorna_id():
    """Testa o retorno do identificador interno da variante importada."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.lastrowid = 50

    conexao.execute.return_value = resultado_execute

    variante = VarianteImportacaoCatalogoDTO(
        app_id=730,
        nome_mercado="★ Bayonet | Doppler (Factory New)",
        fonte="csgo_api",
        id_externo="skin-abc_0",
        skin_id_externo="skin-abc",
        indice_pintura=415,
        identificador_acabamento="doppler",
        nome_variante="Ruby",
    )

    resultado = inserir_ou_atualizar_variante_catalogo_importacao(
        conexao,
        item_catalogo_id=35,
        variante=variante,
    )

    assert resultado == 50

    conexao.execute.assert_called_once()

def test_importacao_variante_envia_parametros_corretos():
    """Testa os parâmetros enviados para persistir uma variante."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.lastrowid = 50

    conexao.execute.return_value = resultado_execute

    variante = VarianteImportacaoCatalogoDTO(
        app_id=730,
        nome_mercado="★ Bayonet | Doppler (Factory New)",
        fonte="csgo_api",
        id_externo="skin-abc_0",
        skin_id_externo="skin-abc",
        indice_pintura=415,
        identificador_acabamento="doppler",
        nome_variante="Ruby",
        url_imagem="https://example.com/bayonet-ruby.png",
    )

    inserir_ou_atualizar_variante_catalogo_importacao(
        conexao,
        item_catalogo_id=35,
        variante=variante,
    )

    argumentos = conexao.execute.call_args
    parametros = argumentos.args[1]

    assert parametros == {
        "item_catalogo_id": 35,
        "fonte": "csgo_api",
        "id_externo": "skin-abc_0",
        "skin_id_externo": "skin-abc",
        "indice_pintura": 415,
        "identificador_acabamento": "doppler",
        "nome_variante": "Ruby",
        "url_imagem": "https://example.com/bayonet-ruby.png",
    }

    conexao.execute.assert_called_once()

def test_importacao_variante_rejeita_item_catalogo_id_invalido():
    """Testa a rejeição de uma variante com item_catalogo_id inválido."""

    conexao = Mock()

    variante = VarianteImportacaoCatalogoDTO(
        app_id=730,
        nome_mercado="★ Bayonet | Doppler (Factory New)",
        fonte="csgo_api",
        id_externo="skin-abc_0",
    )

    with pytest.raises(
        ValueError,
        match="item_catalogo_id",
    ):
        inserir_ou_atualizar_variante_catalogo_importacao(
            conexao,
            item_catalogo_id=0,
            variante=variante,
        )

    conexao.execute.assert_not_called()

def test_importacao_variante_rejeita_app_id_invalido():
    """Testa a rejeição de uma variante com app_id inválido."""

    conexao = Mock()

    variante = VarianteImportacaoCatalogoDTO(
        app_id=0,
        nome_mercado="★ Bayonet | Doppler (Factory New)",
        fonte="csgo_api",
        id_externo="skin-abc_0",
    )

    with pytest.raises(
        ValueError,
        match="app_id",
    ):
        inserir_ou_atualizar_variante_catalogo_importacao(
            conexao,
            item_catalogo_id=35,
            variante=variante,
        )

    conexao.execute.assert_not_called()

def test_importacao_variante_rejeita_nome_mercado_vazio():
    """Testa a rejeição de uma variante sem nome de mercado válido."""

    conexao = Mock()

    variante = VarianteImportacaoCatalogoDTO(
        app_id=730,
        nome_mercado="   ",
        fonte="csgo_api",
        id_externo="skin-abc_0",
    )

    with pytest.raises(
        ValueError,
        match="nome de mercado",
    ):
        inserir_ou_atualizar_variante_catalogo_importacao(
            conexao,
            item_catalogo_id=35,
            variante=variante,
        )

    conexao.execute.assert_not_called()

def test_importacao_variante_rejeita_fonte_vazia():
    """Testa a rejeição de uma variante sem fonte externa válida."""

    conexao = Mock()

    variante = VarianteImportacaoCatalogoDTO(
        app_id=730,
        nome_mercado="★ Bayonet | Doppler (Factory New)",
        fonte="   ",
        id_externo="skin-abc_0",
    )

    with pytest.raises(
        ValueError,
        match="fonte da variante",
    ):
        inserir_ou_atualizar_variante_catalogo_importacao(
            conexao,
            item_catalogo_id=35,
            variante=variante,
        )

    conexao.execute.assert_not_called()

def test_importacao_variante_rejeita_id_externo_vazio():
    """Testa a rejeição de uma variante sem identificador externo válido."""

    conexao = Mock()

    variante = VarianteImportacaoCatalogoDTO(
        app_id=730,
        nome_mercado="★ Bayonet | Doppler (Factory New)",
        fonte="csgo_api",
        id_externo="   ",
    )

    with pytest.raises(
        ValueError,
        match="identificador externo",
    ):
        inserir_ou_atualizar_variante_catalogo_importacao(
            conexao,
            item_catalogo_id=35,
            variante=variante,
        )

    conexao.execute.assert_not_called()

def test_importacao_variante_rejeita_id_nao_retornado():
    """Testa a falha quando a persistência não retorna um ID válido."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.lastrowid = None

    conexao.execute.return_value = resultado_execute

    variante = VarianteImportacaoCatalogoDTO(
        app_id=730,
        nome_mercado="★ Bayonet | Doppler (Factory New)",
        fonte="csgo_api",
        id_externo="skin-abc_0",
    )

    with pytest.raises(
        RuntimeError,
        match="ID da variante importada",
    ):
        inserir_ou_atualizar_variante_catalogo_importacao(
            conexao,
            item_catalogo_id=35,
            variante=variante,
        )

    conexao.execute.assert_called_once()

def test_importacao_variante_utiliza_upsert_mysql():
    """Testa a utilização de upsert para evitar variantes duplicadas."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.lastrowid = 50

    conexao.execute.return_value = resultado_execute

    variante = VarianteImportacaoCatalogoDTO(
        app_id=730,
        nome_mercado="★ Bayonet | Doppler (Factory New)",
        fonte="csgo_api",
        id_externo="skin-abc_0",
    )

    inserir_ou_atualizar_variante_catalogo_importacao(
        conexao,
        item_catalogo_id=35,
        variante=variante,
    )

    argumentos = conexao.execute.call_args

    consulta = str(
        argumentos.args[0]
    )

    assert "ON DUPLICATE KEY UPDATE" in consulta
    assert "LAST_INSERT_ID(id)" in consulta

    conexao.execute.assert_called_once()

def test_importacao_variante_atualiza_vinculo_comercial():
    """Testa a atualização do vínculo da variante com o item comercial."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.lastrowid = 50

    conexao.execute.return_value = resultado_execute

    variante = VarianteImportacaoCatalogoDTO(
        app_id=730,
        nome_mercado="★ Bayonet | Doppler (Factory New)",
        fonte="csgo_api",
        id_externo="skin-abc_0",
    )

    inserir_ou_atualizar_variante_catalogo_importacao(
        conexao,
        item_catalogo_id=35,
        variante=variante,
    )

    argumentos = conexao.execute.call_args

    consulta = str(
        argumentos.args[0]
    )

    parametros = argumentos.args[1]

    assert (
        "item_catalogo_id = VALUES(item_catalogo_id)"
        in consulta
    )

    assert parametros["item_catalogo_id"] == 35

    conexao.execute.assert_called_once()