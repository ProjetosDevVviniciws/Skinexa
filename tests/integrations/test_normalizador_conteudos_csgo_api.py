import pytest

from skinexa.dto.catalogo.conteineres import (
    ConteudoConteinerCatalogoDTO,
)

from skinexa.integrations.catalogo.normalizador_conteudos_csgo_api import (
    ErroNormalizacaoConteudoCSGOAPI,
    normalizar_conteudo_csgo_api,
)

def criar_registro_conteudo_csgo_api(
    *,
    id_externo: str = "skin-2ca8cb95f31e",
    nome: str = "MP7 | Skulls",
    raridade: dict | None = None,
    paint_index: str | int | None = "11",
    fase: str | dict | None = None,
    imagem: str | None = "https://exemplo.com/mp7.png",
) -> dict:
    """Cria um conteúdo simulado da CSGO-API."""

    if raridade is None:
        raridade = {
            "id": "rarity_rare_weapon",
            "name": "Mil-Spec Grade",
        }

    return {
        "id": id_externo,
        "name": nome,
        "rarity": raridade,
        "paint_index": paint_index,
        "phase": fase,
        "image": imagem,
    }

def test_normalizar_conteudo_csgo_api():
    """Testa a normalização de um conteúdo válido."""

    registro = criar_registro_conteudo_csgo_api()

    resultado = normalizar_conteudo_csgo_api(
        registro,
        conteiner_catalogo_id=10,
        tipo_conteudo="contains",
    )

    assert isinstance(
        resultado,
        ConteudoConteinerCatalogoDTO,
    )

    assert resultado.conteiner_catalogo_id == 10
    assert resultado.fonte == "csgo_api"
    assert resultado.id_externo_conteudo == "skin-2ca8cb95f31e"
    assert resultado.nome_conteudo == "MP7 | Skulls"
    assert resultado.tipo_conteudo == "contains"
    assert resultado.raridade == "Mil-Spec Grade"
    assert resultado.indice_pintura == 11
    assert resultado.nome_fase is None
    assert resultado.url_imagem == "https://exemplo.com/mp7.png"

def test_normalizar_conteudo_contains_rare():
    """Testa a normalização de um conteúdo raro."""

    registro = criar_registro_conteudo_csgo_api(
        id_externo="skin-vanilla-weapon_bayonet",
        nome="Bayonet",
        paint_index=None,
    )

    resultado = normalizar_conteudo_csgo_api(
        registro,
        conteiner_catalogo_id=10,
        tipo_conteudo="contains_rare",
    )

    assert resultado.tipo_conteudo == "contains_rare"
    assert resultado.id_externo_conteudo == (
        "skin-vanilla-weapon_bayonet"
    )
    assert resultado.indice_pintura is None

def test_normalizar_conteudo_remove_espacos():
    """Remove espaços dos campos textuais."""

    registro = criar_registro_conteudo_csgo_api(
        id_externo="  skin-2ca8cb95f31e  ",
        nome="  MP7 | Skulls  ",
        raridade={"name": "  Mil-Spec Grade  "},
        fase="  Phase 1  ",
        imagem="  https://exemplo.com/mp7.png  ",
    )

    resultado = normalizar_conteudo_csgo_api(
        registro,
        conteiner_catalogo_id=10,
        tipo_conteudo="  contains  ",
    )

    assert resultado.id_externo_conteudo == "skin-2ca8cb95f31e"
    assert resultado.nome_conteudo == "MP7 | Skulls"
    assert resultado.tipo_conteudo == "contains"
    assert resultado.raridade == "Mil-Spec Grade"
    assert resultado.nome_fase == "Phase 1"
    assert resultado.url_imagem == "https://exemplo.com/mp7.png"

@pytest.mark.parametrize(
    "registro",
    [
        None,
        [],
        "conteudo-invalido",
        123,
    ],
)

def test_normalizar_conteudo_rejeita_registro_invalido(
    registro,
):
    """Rejeita registros que não são dicionários."""

    with pytest.raises(
        ErroNormalizacaoConteudoCSGOAPI,
        match="Registro de conteúdo inválido",
    ):
        normalizar_conteudo_csgo_api(
            registro,
            conteiner_catalogo_id=10,
            tipo_conteudo="contains",
        )

@pytest.mark.parametrize(
    "conteiner_id",
    [0, -1, True, False, "10", None],
)

def test_normalizar_conteudo_rejeita_conteiner_id_invalido(
    conteiner_id,
):
    """Rejeita identificadores internos inválidos."""

    registro = criar_registro_conteudo_csgo_api()

    with pytest.raises(
        ErroNormalizacaoConteudoCSGOAPI,
        match="ID do contêiner inválido",
    ):
        normalizar_conteudo_csgo_api(
            registro,
            conteiner_catalogo_id=conteiner_id,
            tipo_conteudo="contains",
        )

@pytest.mark.parametrize(
    "tipo_conteudo",
    [
        "",
        "   ",
        "rare",
        "outro",
        None,
        123,
    ],
)

def test_normalizar_conteudo_rejeita_tipo_invalido(
    tipo_conteudo,
):
    """Rejeita tipos de conteúdo não suportados."""

    registro = criar_registro_conteudo_csgo_api()

    with pytest.raises(
        ErroNormalizacaoConteudoCSGOAPI,
        match="Tipo de conteúdo não suportado",
    ):
        normalizar_conteudo_csgo_api(
            registro,
            conteiner_catalogo_id=10,
            tipo_conteudo=tipo_conteudo,
        )

@pytest.mark.parametrize(
    "id_externo",
    [None, "", "   ", 123, []],
)

def test_normalizar_conteudo_rejeita_id_externo_invalido(
    id_externo,
):
    """Rejeita IDs externos ausentes ou inválidos."""

    registro = criar_registro_conteudo_csgo_api()
    registro["id"] = id_externo

    with pytest.raises(
        ErroNormalizacaoConteudoCSGOAPI,
        match="Conteúdo sem ID externo válido",
    ):
        normalizar_conteudo_csgo_api(
            registro,
            conteiner_catalogo_id=10,
            tipo_conteudo="contains",
        )

def test_normalizar_conteudo_rejeita_id_externo_longo():
    """Rejeita IDs acima de 150 caracteres."""

    registro = criar_registro_conteudo_csgo_api(
        id_externo="x" * 151,
    )

    with pytest.raises(
        ErroNormalizacaoConteudoCSGOAPI,
        match="ID externo do conteúdo excede 150 caracteres",
    ):
        normalizar_conteudo_csgo_api(
            registro,
            conteiner_catalogo_id=10,
            tipo_conteudo="contains",
        )

def test_normalizar_conteudo_aceita_id_externo_limite():
    """Aceita IDs externos com 150 caracteres."""

    registro = criar_registro_conteudo_csgo_api(
        id_externo="x" * 150,
    )

    resultado = normalizar_conteudo_csgo_api(
        registro,
        conteiner_catalogo_id=10,
        tipo_conteudo="contains",
    )

    assert len(resultado.id_externo_conteudo) == 150

@pytest.mark.parametrize(
    "nome",
    [None, "", "   ", 123, []],
)

def test_normalizar_conteudo_rejeita_nome_invalido(
    nome,
):
    """Rejeita nomes ausentes ou inválidos."""

    registro = criar_registro_conteudo_csgo_api()
    registro["name"] = nome

    with pytest.raises(
        ErroNormalizacaoConteudoCSGOAPI,
        match="Conteúdo sem nome válido",
    ):
        normalizar_conteudo_csgo_api(
            registro,
            conteiner_catalogo_id=10,
            tipo_conteudo="contains",
        )

def test_normalizar_conteudo_rejeita_nome_longo():
    """Rejeita nomes acima de 255 caracteres."""

    registro = criar_registro_conteudo_csgo_api(
        nome="x" * 256,
    )

    with pytest.raises(
        ErroNormalizacaoConteudoCSGOAPI,
        match="Nome do conteúdo excede 255 caracteres",
    ):
        normalizar_conteudo_csgo_api(
            registro,
            conteiner_catalogo_id=10,
            tipo_conteudo="contains",
        )

def test_normalizar_conteudo_aceita_nome_limite():
    """Aceita nomes com exatamente 255 caracteres."""

    registro = criar_registro_conteudo_csgo_api(
        nome="x" * 255,
    )

    resultado = normalizar_conteudo_csgo_api(
        registro,
        conteiner_catalogo_id=10,
        tipo_conteudo="contains",
    )

    assert len(resultado.nome_conteudo) == 255

def test_normalizar_conteudo_sem_raridade():
    """Aceita conteúdos sem raridade informada."""

    registro = criar_registro_conteudo_csgo_api()
    registro["rarity"] = None

    resultado = normalizar_conteudo_csgo_api(
        registro,
        conteiner_catalogo_id=10,
        tipo_conteudo="contains",
    )

    assert resultado.raridade is None

def test_normalizar_conteudo_raridade_invalida():
    """Ignora raridade com estrutura inesperada."""

    registro = criar_registro_conteudo_csgo_api()
    registro["rarity"] = "Mil-Spec Grade"

    resultado = normalizar_conteudo_csgo_api(
        registro,
        conteiner_catalogo_id=10,
        tipo_conteudo="contains",
    )

    assert resultado.raridade is None

def test_normalizar_conteudo_rejeita_raridade_longa():
    """Rejeita raridades acima de 100 caracteres."""

    registro = criar_registro_conteudo_csgo_api(
        raridade={"name": "x" * 101},
    )

    with pytest.raises(
        ErroNormalizacaoConteudoCSGOAPI,
        match="Raridade do conteúdo excede 100 caracteres",
    ):
        normalizar_conteudo_csgo_api(
            registro,
            conteiner_catalogo_id=10,
            tipo_conteudo="contains",
        )

def test_normalizar_conteudo_aceita_raridade_limite():
    """Aceita raridades com 100 caracteres."""

    registro = criar_registro_conteudo_csgo_api(
        raridade={"name": "x" * 100},
    )

    resultado = normalizar_conteudo_csgo_api(
        registro,
        conteiner_catalogo_id=10,
        tipo_conteudo="contains",
    )

    assert len(resultado.raridade) == 100

@pytest.mark.parametrize(
    "paint_index",
    [None, "0", 0, "11", 11, "4294967295", 4294967295],
)

def test_normalizar_conteudo_paint_index_valido(
    paint_index,
):
    """Aceita índices de pintura válidos."""

    registro = criar_registro_conteudo_csgo_api(
        paint_index=paint_index,
    )

    resultado = normalizar_conteudo_csgo_api(
        registro,
        conteiner_catalogo_id=10,
        tipo_conteudo="contains",
    )

    esperado = (
        int(paint_index)
        if paint_index is not None
        else None
    )

    assert resultado.indice_pintura == esperado

@pytest.mark.parametrize(
    "paint_index",
    [
        -1,
        "-1",
        4294967296,
        "4294967296",
        True,
        False,
        "abc",
        "",
        [],
        {},
        1.5,
    ],
)

def test_normalizar_conteudo_paint_index_invalido(
    paint_index,
):
    """Rejeita índices de pintura inválidos."""

    registro = criar_registro_conteudo_csgo_api(
        paint_index=paint_index,
    )

    with pytest.raises(
        ErroNormalizacaoConteudoCSGOAPI,
        match="Índice de pintura",
    ):
        normalizar_conteudo_csgo_api(
            registro,
            conteiner_catalogo_id=10,
            tipo_conteudo="contains",
        )

def test_normalizar_conteudo_fase_textual():
    """Normaliza uma fase fornecida como texto."""

    registro = criar_registro_conteudo_csgo_api(
        fase="Phase 1",
    )

    resultado = normalizar_conteudo_csgo_api(
        registro,
        conteiner_catalogo_id=10,
        tipo_conteudo="contains",
    )

    assert resultado.nome_fase == "Phase 1"

def test_normalizar_conteudo_fase_objeto():
    """Normaliza uma fase fornecida como objeto."""

    registro = criar_registro_conteudo_csgo_api(
        fase={"name": "Phase 2"},
    )

    resultado = normalizar_conteudo_csgo_api(
        registro,
        conteiner_catalogo_id=10,
        tipo_conteudo="contains",
    )

    assert resultado.nome_fase == "Phase 2"

def test_normalizar_conteudo_fase_ausente():
    """Aceita conteúdos sem fase."""

    registro = criar_registro_conteudo_csgo_api(
        fase=None,
    )

    resultado = normalizar_conteudo_csgo_api(
        registro,
        conteiner_catalogo_id=10,
        tipo_conteudo="contains",
    )

    assert resultado.nome_fase is None

def test_normalizar_conteudo_rejeita_fase_longa():
    """Rejeita fases acima de 100 caracteres."""

    registro = criar_registro_conteudo_csgo_api(
        fase="x" * 101,
    )

    with pytest.raises(
        ErroNormalizacaoConteudoCSGOAPI,
        match="Fase do conteúdo excede 100 caracteres",
    ):
        normalizar_conteudo_csgo_api(
            registro,
            conteiner_catalogo_id=10,
            tipo_conteudo="contains",
        )

def test_normalizar_conteudo_aceita_fase_limite():
    """Aceita fases com exatamente 100 caracteres."""

    registro = criar_registro_conteudo_csgo_api(
        fase="x" * 100,
    )

    resultado = normalizar_conteudo_csgo_api(
        registro,
        conteiner_catalogo_id=10,
        tipo_conteudo="contains",
    )

    assert len(resultado.nome_fase) == 100

@pytest.mark.parametrize(
    "imagem",
    [None, "", "   "],
)

def test_normalizar_conteudo_imagem_opcional(
    imagem,
):
    """Aceita conteúdos sem imagem válida."""

    registro = criar_registro_conteudo_csgo_api(
        imagem=imagem,
    )

    resultado = normalizar_conteudo_csgo_api(
        registro,
        conteiner_catalogo_id=10,
        tipo_conteudo="contains",
    )

    assert resultado.url_imagem is None

def test_normalizar_conteudo_nao_modifica_registro():
    """Verifica que o registro original não é alterado."""

    registro = criar_registro_conteudo_csgo_api()
    original = registro.copy()

    normalizar_conteudo_csgo_api(
        registro,
        conteiner_catalogo_id=10,
        tipo_conteudo="contains",
    )

    assert registro == original