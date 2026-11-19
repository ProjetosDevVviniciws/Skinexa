import pytest

from skinexa.dto.catalogo.conteineres import (
    ConteinerCatalogoDTO,
)

from skinexa.integrations.catalogo.normalizador_conteineres_csgo_api import (
    ErroNormalizacaoConteinerCSGOAPI,
    normalizar_conteiner_csgo_api,
)

def criar_registro_conteiner_csgo_api(
    *,
    id_externo: str = "crate-4001",
    nome: str = "CS:GO Weapon Case",
    tipo: str | None = "Case",
    imagem: str | None = "https://exemplo.com/caixa.png",
) -> dict:
    """Cria um registro simulado de contêiner da CSGO-API."""

    return {
        "id": id_externo,
        "name": nome,
        "type": tipo,
        "image": imagem,
    }

def test_normalizar_conteiner_csgo_api():
    """Testa a normalização de um contêiner válido."""

    registro = criar_registro_conteiner_csgo_api()

    resultado = normalizar_conteiner_csgo_api(
        registro
    )

    assert isinstance(
        resultado,
        ConteinerCatalogoDTO,
    )

    assert resultado.fonte == "csgo_api"
    assert resultado.id_externo == "crate-4001"
    assert resultado.nome == "CS:GO Weapon Case"
    assert resultado.tipo_conteiner == "Case"
    assert resultado.url_imagem == (
        "https://exemplo.com/caixa.png"
    )
    assert resultado.item_catalogo_id is None

def test_normalizar_conteiner_remove_espacos():
    """Remove espaços dos campos textuais."""

    registro = criar_registro_conteiner_csgo_api(
        id_externo="  crate-4001  ",
        nome="  CS:GO Weapon Case  ",
        tipo="  Case  ",
        imagem="  https://exemplo.com/caixa.png  ",
    )

    resultado = normalizar_conteiner_csgo_api(
        registro
    )

    assert resultado.id_externo == "crate-4001"
    assert resultado.nome == "CS:GO Weapon Case"
    assert resultado.tipo_conteiner == "Case"
    assert resultado.url_imagem == (
        "https://exemplo.com/caixa.png"
    )

@pytest.mark.parametrize(
    "tipo",
    [
        None,
        "",
        "   ",
    ],
)

def test_normalizar_conteiner_sem_tipo(
    tipo,
):
    """Aceita tipo de contêiner ausente ou vazio."""

    registro = criar_registro_conteiner_csgo_api(
        tipo=tipo,
    )

    resultado = normalizar_conteiner_csgo_api(
        registro
    )

    assert resultado.tipo_conteiner is None

def test_normalizar_conteiner_sem_campo_tipo():
    """Aceita registros sem a chave type."""

    registro = criar_registro_conteiner_csgo_api()
    del registro["type"]

    resultado = normalizar_conteiner_csgo_api(
        registro
    )

    assert resultado.tipo_conteiner is None

@pytest.mark.parametrize(
    "imagem",
    [
        None,
        "",
        "   ",
    ],
)

def test_normalizar_conteiner_sem_imagem(
    imagem,
):
    """Aceita imagem ausente ou vazia."""

    registro = criar_registro_conteiner_csgo_api(
        imagem=imagem,
    )

    resultado = normalizar_conteiner_csgo_api(
        registro
    )

    assert resultado.url_imagem is None

def test_normalizar_conteiner_sem_campo_imagem():
    """Aceita registros sem a chave image."""

    registro = criar_registro_conteiner_csgo_api()
    del registro["image"]

    resultado = normalizar_conteiner_csgo_api(
        registro
    )

    assert resultado.url_imagem is None

@pytest.mark.parametrize(
    "registro",
    [
        None,
        [],
        "conteiner-invalido",
        123,
    ],
)

def test_normalizar_conteiner_rejeita_registro_invalido(
    registro,
):
    """Rejeita registros que não são dicionários."""

    with pytest.raises(
        ErroNormalizacaoConteinerCSGOAPI,
        match="Registro de contêiner inválido",
    ):
        normalizar_conteiner_csgo_api(
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

def test_normalizar_conteiner_rejeita_id_invalido(
    id_externo,
):
    """Rejeita identificadores externos inválidos."""

    registro = criar_registro_conteiner_csgo_api()
    registro["id"] = id_externo

    with pytest.raises(
        ErroNormalizacaoConteinerCSGOAPI,
        match="Contêiner sem ID externo válido",
    ):
        normalizar_conteiner_csgo_api(
            registro
        )

def test_normalizar_conteiner_rejeita_id_muito_longo():
    """Rejeita identificadores acima de 150 caracteres."""

    registro = criar_registro_conteiner_csgo_api(
        id_externo="x" * 151,
    )

    with pytest.raises(
        ErroNormalizacaoConteinerCSGOAPI,
        match="ID externo do contêiner excede 150 caracteres",
    ):
        normalizar_conteiner_csgo_api(
            registro
        )

def test_normalizar_conteiner_aceita_id_limite():
    """Aceita identificadores com exatamente 150 caracteres."""

    registro = criar_registro_conteiner_csgo_api(
        id_externo="x" * 150,
    )

    resultado = normalizar_conteiner_csgo_api(
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

def test_normalizar_conteiner_rejeita_nome_invalido(
    nome,
):
    """Rejeita nomes ausentes ou inválidos."""

    registro = criar_registro_conteiner_csgo_api()
    registro["name"] = nome

    with pytest.raises(
        ErroNormalizacaoConteinerCSGOAPI,
        match="Contêiner sem nome válido",
    ):
        normalizar_conteiner_csgo_api(
            registro
        )

def test_normalizar_conteiner_rejeita_nome_muito_longo():
    """Rejeita nomes acima de 255 caracteres."""

    registro = criar_registro_conteiner_csgo_api(
        nome="x" * 256,
    )

    with pytest.raises(
        ErroNormalizacaoConteinerCSGOAPI,
        match="Nome do contêiner excede 255 caracteres",
    ):
        normalizar_conteiner_csgo_api(
            registro
        )

def test_normalizar_conteiner_aceita_nome_limite():
    """Aceita nomes com exatamente 255 caracteres."""

    registro = criar_registro_conteiner_csgo_api(
        nome="x" * 255,
    )

    resultado = normalizar_conteiner_csgo_api(
        registro
    )

    assert len(resultado.nome) == 255

def test_normalizar_conteiner_rejeita_tipo_muito_longo():
    """Rejeita tipos acima de 100 caracteres."""

    registro = criar_registro_conteiner_csgo_api(
        tipo="x" * 101,
    )

    with pytest.raises(
        ErroNormalizacaoConteinerCSGOAPI,
        match="Tipo do contêiner excede 100 caracteres",
    ):
        normalizar_conteiner_csgo_api(
            registro
        )

def test_normalizar_conteiner_aceita_tipo_limite():
    """Aceita tipos com exatamente 100 caracteres."""

    registro = criar_registro_conteiner_csgo_api(
        tipo="x" * 100,
    )

    resultado = normalizar_conteiner_csgo_api(
        registro
    )

    assert len(resultado.tipo_conteiner) == 100

def test_normalizar_conteiner_nao_inferir_item_comercial():
    """Não associa um contêiner a um item comercial automaticamente."""

    registro = criar_registro_conteiner_csgo_api()

    registro["market_hash_name"] = "CS:GO Weapon Case"

    resultado = normalizar_conteiner_csgo_api(
        registro
    )

    assert resultado.item_catalogo_id is None

def test_normalizar_conteiner_nao_modifica_registro():
    """Preserva o registro original recebido da API."""

    registro = criar_registro_conteiner_csgo_api()

    original = registro.copy()

    normalizar_conteiner_csgo_api(
        registro
    )

    assert registro == original