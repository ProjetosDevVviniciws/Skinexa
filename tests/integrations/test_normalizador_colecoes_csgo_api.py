import pytest

from skinexa.dto.catalogo.colecoes import (
    ColecaoCatalogoDTO,
)

from skinexa.integrations.catalogo.normalizador_colecoes_csgo_api import (
    ErroNormalizacaoColecaoCSGOAPI,
    extrair_skin_ids_colecao_csgo_api,
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
    
def criar_registro_colecao_com_skins(
    *,
    conteudos: list | None = None,
) -> dict:
    """Cria uma coleção simulada com relacionamentos."""

    if conteudos is None:
        conteudos = [
            {"id": "skin-ak47"},
            {"id": "skin-awp"},
        ]

    return {
        "id": "collection-test",
        "name": "Test Collection",
        "contains": conteudos,
    }

def test_extrair_skin_ids_colecao_csgo_api():
    """Extrai todos os identificadores das skins."""

    registro = criar_registro_colecao_com_skins()

    resultado = extrair_skin_ids_colecao_csgo_api(
        registro
    )

    assert resultado == {
        "skin-ak47",
        "skin-awp",
    }

def test_extrair_skin_ids_remove_duplicacoes():
    """Remove identificadores repetidos na coleção."""

    registro = criar_registro_colecao_com_skins(
        conteudos=[
            {"id": "skin-ak47"},
            {"id": "skin-awp"},
            {"id": "skin-ak47"},
        ],
    )

    resultado = extrair_skin_ids_colecao_csgo_api(
        registro
    )

    assert resultado == {
        "skin-ak47",
        "skin-awp",
    }

def test_extrair_skin_ids_normaliza_espacos():
    """Remove espaços antes de registrar os identificadores."""

    registro = criar_registro_colecao_com_skins(
        conteudos=[
            {"id": "  skin-ak47  "},
            {"id": " skin-awp "},
        ],
    )

    resultado = extrair_skin_ids_colecao_csgo_api(
        registro
    )

    assert resultado == {
        "skin-ak47",
        "skin-awp",
    }

def test_extrair_skin_ids_colecao_vazia():
    """Aceita uma lista de conteúdos vazia."""

    registro = criar_registro_colecao_com_skins(
        conteudos=[],
    )

    resultado = extrair_skin_ids_colecao_csgo_api(
        registro
    )

    assert resultado == set()

@pytest.mark.parametrize(
    "conteudos",
    [
        None,
        {},
        "",
        "skin-ak47",
        123,
    ],
)

def test_extrair_skin_ids_rejeita_contains_invalido(
    conteudos,
):
    """Rejeita relacionamentos que não são listas."""

    registro = criar_registro_colecao_com_skins()
    registro["contains"] = conteudos

    with pytest.raises(
        ErroNormalizacaoColecaoCSGOAPI,
        match="Relacionamentos da coleção inválidos",
    ):
        extrair_skin_ids_colecao_csgo_api(
            registro
        )

def test_extrair_skin_ids_rejeita_contains_ausente():
    """Rejeita coleções sem o campo contains."""

    registro = criar_registro_colecao_com_skins()
    del registro["contains"]

    with pytest.raises(
        ErroNormalizacaoColecaoCSGOAPI,
        match="Relacionamentos da coleção inválidos",
    ):
        extrair_skin_ids_colecao_csgo_api(
            registro
        )

@pytest.mark.parametrize(
    "conteudo",
    [
        None,
        [],
        "skin-ak47",
        123,
    ],
)

def test_extrair_skin_ids_rejeita_conteudo_invalido(
    conteudo,
):
    """Rejeita elementos de contains que não são objetos."""

    registro = criar_registro_colecao_com_skins(
        conteudos=[conteudo],
    )

    with pytest.raises(
        ErroNormalizacaoColecaoCSGOAPI,
        match="Conteúdo inválido na coleção",
    ):
        extrair_skin_ids_colecao_csgo_api(
            registro
        )

@pytest.mark.parametrize(
    "skin_id",
    [
        None,
        "",
        "   ",
        123,
        [],
    ],
)

def test_extrair_skin_ids_rejeita_id_invalido(
    skin_id,
):
    """Rejeita skins sem identificador textual válido."""

    registro = criar_registro_colecao_com_skins(
        conteudos=[
            {"id": skin_id},
        ],
    )

    with pytest.raises(
        ErroNormalizacaoColecaoCSGOAPI,
        match="Skin sem identificador válido",
    ):
        extrair_skin_ids_colecao_csgo_api(
            registro
        )

def test_extrair_skin_ids_rejeita_id_muito_longo():
    """Rejeita skin_ids acima de 150 caracteres."""

    registro = criar_registro_colecao_com_skins(
        conteudos=[
            {"id": "x" * 151},
        ],
    )

    with pytest.raises(
        ErroNormalizacaoColecaoCSGOAPI,
        match="Identificador da skin excede 150 caracteres",
    ):
        extrair_skin_ids_colecao_csgo_api(
            registro
        )

def test_extrair_skin_ids_aceita_id_limite():
    """Aceita skin_ids com exatamente 150 caracteres."""

    registro = criar_registro_colecao_com_skins(
        conteudos=[
            {"id": "x" * 150},
        ],
    )

    resultado = extrair_skin_ids_colecao_csgo_api(
        registro
    )

    assert resultado == {"x" * 150}

@pytest.mark.parametrize(
    "registro",
    [
        None,
        [],
        "colecao-invalida",
        123,
    ],
)

def test_extrair_skin_ids_rejeita_registro_invalido(
    registro,
):
    """Rejeita registros que não são dicionários."""

    with pytest.raises(
        ErroNormalizacaoColecaoCSGOAPI,
        match="Registro de coleção inválido",
    ):
        extrair_skin_ids_colecao_csgo_api(
            registro
        )

def test_extrair_skin_ids_rejeita_colecao_invalida():
    """Valida a coleção antes de extrair relacionamentos."""

    registro = {
        "id": "",
        "name": "Test Collection",
        "contains": [
            {"id": "skin-ak47"},
        ],
    }

    with pytest.raises(
        ErroNormalizacaoColecaoCSGOAPI,
        match="Coleção sem ID externo válido",
    ):
        extrair_skin_ids_colecao_csgo_api(
            registro
        )

def test_extrair_skin_ids_preserva_registro_original():
    """Não modifica o registro recebido da API."""

    registro = criar_registro_colecao_com_skins(
        conteudos=[
            {"id": "  skin-ak47  "},
            {"id": "skin-awp"},
        ],
    )

    import copy

    original = copy.deepcopy(registro)

    extrair_skin_ids_colecao_csgo_api(
        registro
    )

    assert registro == original

def test_extrair_skin_ids_permite_multiplas_colecoes():
    """Permite que uma skin apareça em coleções diferentes."""

    primeira_colecao = {
        "id": "collection-a",
        "name": "Collection A",
        "contains": [
            {"id": "skin-ak47"},
        ],
    }

    segunda_colecao = {
        "id": "collection-b",
        "name": "Collection B",
        "contains": [
            {"id": "skin-ak47"},
        ],
    }

    resultado_primeira = extrair_skin_ids_colecao_csgo_api(
        primeira_colecao
    )

    resultado_segunda = extrair_skin_ids_colecao_csgo_api(
        segunda_colecao
    )

    assert resultado_primeira == {"skin-ak47"}
    assert resultado_segunda == {"skin-ak47"}