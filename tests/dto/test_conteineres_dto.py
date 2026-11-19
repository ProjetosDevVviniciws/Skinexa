from dataclasses import FrozenInstanceError

import pytest

from skinexa.dto.catalogo.conteineres import (
    ConteinerCatalogoDTO,
    ConteudoConteinerCatalogoDTO,
)

def test_criar_conteiner_catalogo_dto():
    """Testa a criação de um contêiner sem vínculo comercial."""

    conteiner = ConteinerCatalogoDTO(
        fonte="csgo_api",
        id_externo="crate-4001",
        nome="CS:GO Weapon Case",
    )

    assert conteiner.fonte == "csgo_api"
    assert conteiner.id_externo == "crate-4001"
    assert conteiner.nome == "CS:GO Weapon Case"

    assert conteiner.item_catalogo_id is None
    assert conteiner.tipo_conteiner is None
    assert conteiner.url_imagem is None

def test_criar_conteiner_catalogo_dto_com_opcionais():
    """Testa contêiner com associação comercial conhecida."""

    conteiner = ConteinerCatalogoDTO(
        fonte="csgo_api",
        id_externo="crate-4001",
        nome="CS:GO Weapon Case",
        item_catalogo_id=100,
        tipo_conteiner="Case",
        url_imagem="https://exemplo.com/caixa.png",
    )

    assert conteiner.item_catalogo_id == 100
    assert conteiner.tipo_conteiner == "Case"
    assert conteiner.url_imagem == "https://exemplo.com/caixa.png"

def test_criar_conteudo_conteiner_catalogo_dto():
    """Testa a criação de um conteúdo com campos obrigatórios."""

    conteudo = ConteudoConteinerCatalogoDTO(
        conteiner_catalogo_id=10,
        fonte="csgo_api",
        id_externo_conteudo="skin-2ca8cb95f31e",
        nome_conteudo="MP7 | Skulls",
        tipo_conteudo="contains",
    )

    assert conteudo.conteiner_catalogo_id == 10
    assert conteudo.fonte == "csgo_api"
    assert conteudo.id_externo_conteudo == "skin-2ca8cb95f31e"
    assert conteudo.nome_conteudo == "MP7 | Skulls"
    assert conteudo.tipo_conteudo == "contains"

    assert conteudo.raridade is None
    assert conteudo.indice_pintura is None
    assert conteudo.nome_fase is None
    assert conteudo.url_imagem is None

def test_criar_conteudo_conteiner_com_opcionais():
    """Testa conteúdo com dados complementares."""

    conteudo = ConteudoConteinerCatalogoDTO(
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

    assert conteudo.raridade == "Mil-Spec Grade"
    assert conteudo.indice_pintura == 11
    assert conteudo.nome_fase == "Phase 1"
    assert conteudo.url_imagem == "https://exemplo.com/mp7.png"

def test_criar_conteudo_conteiner_contains_rare():
    """Testa a representação de um conteúdo raro."""

    conteudo = ConteudoConteinerCatalogoDTO(
        conteiner_catalogo_id=10,
        fonte="csgo_api",
        id_externo_conteudo="skin-vanilla-weapon_bayonet",
        nome_conteudo="Bayonet",
        tipo_conteudo="contains_rare",
    )

    assert conteudo.tipo_conteudo == "contains_rare"

@pytest.mark.parametrize(
    "classe, argumentos, atributo",
    [
        (
            ConteinerCatalogoDTO,
            {
                "fonte": "csgo_api",
                "id_externo": "crate-4001",
                "nome": "CS:GO Weapon Case",
            },
            "fonte",
        ),
        (
            ConteudoConteinerCatalogoDTO,
            {
                "conteiner_catalogo_id": 10,
                "fonte": "csgo_api",
                "id_externo_conteudo": "skin-test",
                "nome_conteudo": "Item de teste",
                "tipo_conteudo": "contains",
            },
            "fonte",
        ),
    ],
)

def test_dtos_conteineres_sao_imutaveis(
    classe,
    argumentos,
    atributo,
):
    """Verifica que os atributos dos DTOs são imutáveis."""

    dto = classe(**argumentos)

    with pytest.raises(FrozenInstanceError):
        setattr(dto, atributo, "outra_fonte")

@pytest.mark.parametrize(
    "classe, argumentos",
    [
        (
            ConteinerCatalogoDTO,
            {
                "fonte": "csgo_api",
                "id_externo": "crate-4001",
                "nome": "CS:GO Weapon Case",
            },
        ),
        (
            ConteudoConteinerCatalogoDTO,
            {
                "conteiner_catalogo_id": 10,
                "fonte": "csgo_api",
                "id_externo_conteudo": "skin-test",
                "nome_conteudo": "Item de teste",
                "tipo_conteudo": "contains",
            },
        ),
    ],
)

def test_dtos_conteineres_utilizam_slots(
    classe,
    argumentos,
):
    """Verifica que os DTOs não possuem dicionário de instância."""

    dto = classe(**argumentos)

    assert not hasattr(dto, "__dict__")