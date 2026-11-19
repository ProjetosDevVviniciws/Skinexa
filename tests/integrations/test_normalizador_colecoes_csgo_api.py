import pytest

from skinexa.dto.catalogo.colecoes import (
    ColecaoCatalogoDTO,
)

from skinexa.integrations.catalogo.normalizador_colecoes_csgo_api import (
    ErroNormalizacaoColecaoCSGOAPI,
    normalizar_colecao_csgo_api,
)

def criar_registro_colecao_csgo_api(
    *,
    id_externo: str = "collection-set-fruits-veggies",
    nome: str = "Fruits And Veggies Sticker Collection",
    imagem: str | None = "https://exemplo.com/colecao.png",
) -> dict:
    """Cria um registro simulado de coleção da CSGO-API."""

    return {
        "id": id_externo,
        "name": nome,
        "image": imagem,
    }

def test_normalizar_colecao_csgo_api():
    """Testa a normalização de uma coleção válida."""

    registro = criar_registro_colecao_csgo_api()

    resultado = normalizar_colecao_csgo_api(
        registro
    )

    assert isinstance(
        resultado,
        ColecaoCatalogoDTO,
    )

    assert resultado.fonte == "csgo_api"
    assert resultado.id_externo == (
        "collection-set-fruits-veggies"
    )
    assert resultado.nome == (
        "Fruits And Veggies Sticker Collection"
    )
    assert resultado.url_imagem == (
        "https://exemplo.com/colecao.png"
    )
    assert resultado.tipo_colecao is None

def test_normalizar_colecao_remove_espacos():
    """Remove espaços dos campos textuais."""

    registro = criar_registro_colecao_csgo_api(
        id_externo="  collection-set-fruits-veggies  ",
        nome="  Fruits And Veggies Sticker Collection  ",
        imagem="  https://exemplo.com/colecao.png  ",
    )

    resultado = normalizar_colecao_csgo_api(
        registro
    )

    assert resultado.id_externo == (
        "collection-set-fruits-veggies"
    )
    assert resultado.nome == (
        "Fruits And Veggies Sticker Collection"
    )
    assert resultado.url_imagem == (
        "https://exemplo.com/colecao.png"
    )

def test_normalizar_colecao_sem_imagem():
    """Aceita coleções sem imagem disponível."""

    registro = criar_registro_colecao_csgo_api(
        imagem=None,
    )

    resultado = normalizar_colecao_csgo_api(
        registro
    )

    assert resultado.url_imagem is None

def test_normalizar_colecao_com_imagem_vazia():
    """Converte imagem vazia em None."""

    registro = criar_registro_colecao_csgo_api(
        imagem="   ",
    )

    resultado = normalizar_colecao_csgo_api(
        registro
    )

    assert resultado.url_imagem is None

def test_normalizar_colecao_sem_campo_imagem():
    """Aceita registros sem a chave image."""

    registro = criar_registro_colecao_csgo_api()

    del registro["image"]

    resultado = normalizar_colecao_csgo_api(
        registro
    )

    assert resultado.url_imagem is None

@pytest.mark.parametrize(
    "registro",
    [
        None,
        [],
        "colecao-invalida",
        123,
    ],
)

def test_normalizar_colecao_rejeita_registro_invalido(
    registro,
):
    """Rejeita registros que não são dicionários."""

    with pytest.raises(
        ErroNormalizacaoColecaoCSGOAPI,
        match="Registro de coleção inválido",
    ):
        normalizar_colecao_csgo_api(
            registro
        )

@pytest.mark.parametrize(
    "id_externo",
    [
        None,
        "",
        "   ",
        123,
        [],
    ],
)

def test_normalizar_colecao_rejeita_id_invalido(
    id_externo,
):
    """Rejeita identificadores externos inválidos."""

    registro = criar_registro_colecao_csgo_api()

    registro["id"] = id_externo

    with pytest.raises(
        ErroNormalizacaoColecaoCSGOAPI,
        match="Coleção sem ID externo válido",
    ):
        normalizar_colecao_csgo_api(
            registro
        )

def test_normalizar_colecao_rejeita_id_muito_longo():
    """Rejeita IDs externos acima do limite do banco."""

    registro = criar_registro_colecao_csgo_api(
        id_externo="x" * 151,
    )

    with pytest.raises(
        ErroNormalizacaoColecaoCSGOAPI,
        match="ID externo da coleção excede 150 caracteres",
    ):
        normalizar_colecao_csgo_api(
            registro
        )

def test_normalizar_colecao_aceita_id_limite():
    """Aceita identificadores com exatamente 150 caracteres."""

    registro = criar_registro_colecao_csgo_api(
        id_externo="x" * 150,
    )

    resultado = normalizar_colecao_csgo_api(
        registro
    )

    assert len(resultado.id_externo) == 150

@pytest.mark.parametrize(
    "nome",
    [
        None,
        "",
        "   ",
        123,
        [],
    ],
)

def test_normalizar_colecao_rejeita_nome_invalido(
    nome,
):
    """Rejeita nomes ausentes ou inválidos."""

    registro = criar_registro_colecao_csgo_api()

    registro["name"] = nome

    with pytest.raises(
        ErroNormalizacaoColecaoCSGOAPI,
        match="Coleção sem nome válido",
    ):
        normalizar_colecao_csgo_api(
            registro
        )

def test_normalizar_colecao_rejeita_nome_muito_longo():
    """Rejeita nomes acima do limite do banco."""

    registro = criar_registro_colecao_csgo_api(
        nome="x" * 256,
    )

    with pytest.raises(
        ErroNormalizacaoColecaoCSGOAPI,
        match="Nome da coleção excede 255 caracteres",
    ):
        normalizar_colecao_csgo_api(
            registro
        )

def test_normalizar_colecao_aceita_nome_limite():
    """Aceita nomes com exatamente 255 caracteres."""

    registro = criar_registro_colecao_csgo_api(
        nome="x" * 255,
    )

    resultado = normalizar_colecao_csgo_api(
        registro
    )

    assert len(resultado.nome) == 255

def test_normalizar_colecao_nao_inferir_tipo():
    """Não atribui uma classificação sem dados explícitos."""

    registro = criar_registro_colecao_csgo_api(
        nome="Fruits And Veggies Sticker Collection",
    )

    resultado = normalizar_colecao_csgo_api(
        registro
    )

    assert resultado.tipo_colecao is None

def test_normalizar_colecao_nao_modifica_registro():
    """Preserva o dicionário original recebido da API."""

    registro = criar_registro_colecao_csgo_api()

    original = registro.copy()

    normalizar_colecao_csgo_api(
        registro
    )

    assert registro == original