from unittest.mock import Mock

import pytest

from skinexa.database.queries.colecoes_catalogo import (
    contar_colecoes_catalogo,
    inserir_ou_atualizar_colecao_catalogo,
    obter_colecao_catalogo_por_id_externo,
)

def criar_registro_colecao_catalogo(
    *,
    colecao_id: int = 1,
    fonte: str = "csgo_api",
    id_externo: str = "collection-set-fruits-veggies",
    nome: str = "Fruits And Veggies Sticker Collection",
) -> dict:
    """Cria um registro simulado de coleção."""

    return {
        "id": colecao_id,
        "fonte": fonte,
        "id_externo": id_externo,
        "nome": nome,
        "tipo_colecao": None,
        "url_imagem": None,
        "criado_em": None,
        "atualizado_em": None,
    }

def test_obter_colecao_catalogo_por_id_externo():
    """Testa a obtenção de uma coleção pela identidade externa."""

    conexao = Mock()

    registro = criar_registro_colecao_catalogo()

    resultado_execute = Mock()
    resultado_execute.mappings.return_value.first.return_value = (
        registro
    )

    conexao.execute.return_value = resultado_execute

    resultado = obter_colecao_catalogo_por_id_externo(
        conexao,
        fonte="csgo_api",
        id_externo="collection-set-fruits-veggies",
    )

    assert resultado == registro

    conexao.execute.assert_called_once()

def test_obter_colecao_catalogo_inexistente():
    """Retorna None quando a coleção não existe."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.mappings.return_value.first.return_value = None

    conexao.execute.return_value = resultado_execute

    resultado = obter_colecao_catalogo_por_id_externo(
        conexao,
        fonte="csgo_api",
        id_externo="collection-inexistente",
    )

    assert resultado is None

    conexao.execute.assert_called_once()

def test_obter_colecao_catalogo_normaliza_parametros():
    """Remove espaços dos identificadores da consulta."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.mappings.return_value.first.return_value = None

    conexao.execute.return_value = resultado_execute

    obter_colecao_catalogo_por_id_externo(
        conexao,
        fonte="  csgo_api  ",
        id_externo="  collection-set-fruits-veggies  ",
    )

    parametros = conexao.execute.call_args.args[1]

    assert parametros == {
        "fonte": "csgo_api",
        "id_externo": "collection-set-fruits-veggies",
    }

@pytest.mark.parametrize(
    ("fonte", "id_externo"),
    [
        ("   ", "collection-set-fruits-veggies"),
        ("csgo_api", "   "),
        ("   ", "   "),
    ],
)

def test_obter_colecao_catalogo_com_identidade_invalida(
    fonte,
    id_externo,
):
    """Não consulta o banco quando a identidade é inválida."""

    conexao = Mock()

    resultado = obter_colecao_catalogo_por_id_externo(
        conexao,
        fonte=fonte,
        id_externo=id_externo,
    )

    assert resultado is None

    conexao.execute.assert_not_called()

def test_importacao_colecao_retorna_id():
    """Testa o retorno do ID interno da coleção."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.lastrowid = 15

    conexao.execute.return_value = resultado_execute

    resultado = inserir_ou_atualizar_colecao_catalogo(
        conexao,
        fonte="csgo_api",
        id_externo="collection-set-fruits-veggies",
        nome="Fruits And Veggies Sticker Collection",
    )

    assert resultado == 15

    conexao.execute.assert_called_once()

def test_importacao_colecao_envia_parametros():
    """Testa os parâmetros enviados ao banco."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.lastrowid = 15

    conexao.execute.return_value = resultado_execute

    inserir_ou_atualizar_colecao_catalogo(
        conexao,
        fonte="csgo_api",
        id_externo="collection-set-fruits-veggies",
        nome="Fruits And Veggies Sticker Collection",
        tipo_colecao="adesivo",
        url_imagem="https://exemplo.com/colecao.png",
    )

    parametros = conexao.execute.call_args.args[1]

    assert parametros == {
        "fonte": "csgo_api",
        "id_externo": "collection-set-fruits-veggies",
        "nome": "Fruits And Veggies Sticker Collection",
        "tipo_colecao": "adesivo",
        "url_imagem": "https://exemplo.com/colecao.png",
    }

def test_importacao_colecao_remove_espacos():
    """Normaliza os campos textuais antes da persistência."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.lastrowid = 15

    conexao.execute.return_value = resultado_execute

    inserir_ou_atualizar_colecao_catalogo(
        conexao,
        fonte="  csgo_api  ",
        id_externo="  collection-set-fruits-veggies  ",
        nome="  Fruits And Veggies Sticker Collection  ",
        tipo_colecao="  adesivo  ",
        url_imagem="  https://exemplo.com/colecao.png  ",
    )

    parametros = conexao.execute.call_args.args[1]

    assert parametros == {
        "fonte": "csgo_api",
        "id_externo": "collection-set-fruits-veggies",
        "nome": "Fruits And Veggies Sticker Collection",
        "tipo_colecao": "adesivo",
        "url_imagem": "https://exemplo.com/colecao.png",
    }

def test_importacao_colecao_normaliza_opcionais_vazios():
    """Converte campos opcionais vazios em None."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.lastrowid = 15

    conexao.execute.return_value = resultado_execute

    inserir_ou_atualizar_colecao_catalogo(
        conexao,
        fonte="csgo_api",
        id_externo="collection-set-fruits-veggies",
        nome="Fruits And Veggies Sticker Collection",
        tipo_colecao="   ",
        url_imagem="   ",
    )

    parametros = conexao.execute.call_args.args[1]

    assert parametros["tipo_colecao"] is None
    assert parametros["url_imagem"] is None

@pytest.mark.parametrize(
    ("fonte", "id_externo", "nome", "mensagem"),
    [
        (
            "   ",
            "collection-set-fruits-veggies",
            "Fruits And Veggies Sticker Collection",
            "fonte da coleção",
        ),
        (
            "csgo_api",
            "   ",
            "Fruits And Veggies Sticker Collection",
            "ID externo da coleção",
        ),
        (
            "csgo_api",
            "collection-set-fruits-veggies",
            "   ",
            "nome da coleção",
        ),
    ],
)

def test_importacao_colecao_rejeita_campos_obrigatorios_vazios(
    fonte,
    id_externo,
    nome,
    mensagem,
):
    """Rejeita campos obrigatórios inválidos."""

    conexao = Mock()

    with pytest.raises(
        ValueError,
        match=mensagem,
    ):
        inserir_ou_atualizar_colecao_catalogo(
            conexao,
            fonte=fonte,
            id_externo=id_externo,
            nome=nome,
        )

    conexao.execute.assert_not_called()

def test_importacao_colecao_rejeita_id_nao_retornado():
    """Testa falha quando a persistência não retorna ID."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.lastrowid = None

    conexao.execute.return_value = resultado_execute

    with pytest.raises(
        RuntimeError,
        match="ID da coleção",
    ):
        inserir_ou_atualizar_colecao_catalogo(
            conexao,
            fonte="csgo_api",
            id_externo="collection-set-fruits-veggies",
            nome="Fruits And Veggies Sticker Collection",
        )

    conexao.execute.assert_called_once()

def test_importacao_colecao_rejeita_id_zero():
    """Rejeita identificador interno inválido."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.lastrowid = 0

    conexao.execute.return_value = resultado_execute

    with pytest.raises(
        RuntimeError,
        match="ID da coleção",
    ):
        inserir_ou_atualizar_colecao_catalogo(
            conexao,
            fonte="csgo_api",
            id_externo="collection-set-fruits-veggies",
            nome="Fruits And Veggies Sticker Collection",
        )

    conexao.execute.assert_called_once()

def test_importacao_colecao_utiliza_upsert_mysql():
    """Verifica a estratégia SQL de inserção ou atualização."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.lastrowid = 15

    conexao.execute.return_value = resultado_execute

    inserir_ou_atualizar_colecao_catalogo(
        conexao,
        fonte="csgo_api",
        id_externo="collection-set-fruits-veggies",
        nome="Fruits And Veggies Sticker Collection",
    )

    consulta = str(conexao.execute.call_args.args[0])

    assert "ON DUPLICATE KEY UPDATE" in consulta
    assert "LAST_INSERT_ID(id)" in consulta

    assert "nome = VALUES(nome)" in consulta

    assert "tipo_colecao = COALESCE(" in consulta
    assert "url_imagem = COALESCE(" in consulta

    conexao.execute.assert_called_once()

def test_contar_colecoes_catalogo():
    """Testa a contagem total de coleções."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.scalar_one.return_value = 94

    conexao.execute.return_value = resultado_execute

    resultado = contar_colecoes_catalogo(
        conexao,
    )

    assert resultado == 94

    conexao.execute.assert_called_once()

def test_contar_colecoes_catalogo_vazio():
    """Testa a contagem quando não existem coleções."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.scalar_one.return_value = 0

    conexao.execute.return_value = resultado_execute

    resultado = contar_colecoes_catalogo(
        conexao,
    )

    assert resultado == 0

    conexao.execute.assert_called_once()