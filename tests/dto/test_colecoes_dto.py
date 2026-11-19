from dataclasses import FrozenInstanceError

import pytest

from skinexa.dto.catalogo.colecoes import (
    ColecaoCatalogoDTO,
    RelacaoItemColecaoDTO,
)

def test_criar_colecao_catalogo_dto():
    """Testa a criação de uma coleção com campos obrigatórios."""

    colecao = ColecaoCatalogoDTO(
        fonte="csgo_api",
        id_externo="collection-set-fruits-veggies",
        nome="Fruits And Veggies Sticker Collection",
    )

    assert colecao.fonte == "csgo_api"
    assert colecao.id_externo == "collection-set-fruits-veggies"
    assert colecao.nome == "Fruits And Veggies Sticker Collection"
    assert colecao.tipo_colecao is None
    assert colecao.url_imagem is None

def test_criar_colecao_catalogo_dto_com_opcionais():
    """Testa uma coleção com informações opcionais."""

    colecao = ColecaoCatalogoDTO(
        fonte="csgo_api",
        id_externo="collection-set-fruits-veggies",
        nome="Fruits And Veggies Sticker Collection",
        tipo_colecao="adesivo",
        url_imagem="https://exemplo.com/colecao.png",
    )

    assert colecao.tipo_colecao == "adesivo"
    assert colecao.url_imagem == "https://exemplo.com/colecao.png"

def test_criar_relacao_item_colecao_dto():
    """Testa a representação de uma associação entre item e coleção."""

    relacao = RelacaoItemColecaoDTO(
        item_catalogo_id=100,
        colecao_catalogo_id=10,
        fonte_relacao="csgo_api",
    )

    assert relacao.item_catalogo_id == 100
    assert relacao.colecao_catalogo_id == 10
    assert relacao.fonte_relacao == "csgo_api"

@pytest.mark.parametrize(
    "classe, argumentos, atributo",
    [
        (
            ColecaoCatalogoDTO,
            {
                "fonte": "csgo_api",
                "id_externo": "collection-test",
                "nome": "Coleção de teste",
            },
            "fonte",
        ),
        (
            RelacaoItemColecaoDTO,
            {
                "item_catalogo_id": 100,
                "colecao_catalogo_id": 10,
                "fonte_relacao": "csgo_api",
            },
            "fonte_relacao",
        ),
    ],
)

def test_dtos_colecao_sao_imutaveis(
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
            ColecaoCatalogoDTO,
            {
                "fonte": "csgo_api",
                "id_externo": "collection-test",
                "nome": "Coleção de teste",
            },
        ),
        (
            RelacaoItemColecaoDTO,
            {
                "item_catalogo_id": 100,
                "colecao_catalogo_id": 10,
                "fonte_relacao": "csgo_api",
            },
        ),
    ],
)

def test_dtos_colecao_utilizam_slots(
    classe,
    argumentos,
):
    """Verifica que os DTOs não possuem dicionário de instância."""

    dto = classe(**argumentos)

    assert not hasattr(dto, "__dict__")