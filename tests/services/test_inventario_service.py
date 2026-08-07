from contextlib import nullcontext
from unittest.mock import MagicMock, patch

import pytest

from skinexa.dto.steam.inventario import (
    InstanciaItemSteamDTO,
    ItemCatalogoSteamDTO,
    ItemInventarioSteamDTO,
)
from skinexa.integrations.steam.inventario import InventarioSteamBruto
from skinexa.services.inventory.service import InventarioService

STEAM_ID_TESTE = "76561198000000001"

def criar_item_normalizado() -> ItemInventarioSteamDTO:
    """Cria um item normalizado para testes."""
    catalogo = ItemCatalogoSteamDTO(
        app_id=730,
        nome_mercado="AK-47 | Redline (Field-Tested)",
        nome_exibicao="AK-47 | Redline",
        tipo_item="Rifle",
        nome_arma="AK-47",
        nome_acabamento="Redline",
        estado_exterior="Field-Tested",
        raridade="Classified",
        qualidade=None,
        colecao="The Phoenix Collection",
        descricao=None,
        indice_pintura=None,
        float_minimo=None,
        float_maximo=None,
        variante_stattrak=False,
        variante_souvenir=False,
        comercializavel=True,
        trocavel=True,
        mercadoria_generica=False,
        steam_class_id="2001",
        steam_instance_id="0",
        url_icone=None,
        url_icone_grande=None,
        tags=(),
        metadados_origem={},
    )

    instancia = InstanciaItemSteamDTO(
        steam_id_usuario=STEAM_ID_TESTE,
        app_id=730,
        contexto_id="2",
        asset_id="1001",
        class_id="2001",
        instance_id="0",
        quantidade=1,
        indice_definicao=None,
        indice_pintura=None,
        semente_pintura=None,
        valor_float=None,
        nome_personalizado=None,
        link_inspecao=None,
        stattrak=False,
        contador_stattrak=None,
        souvenir=False,
        trocavel=True,
        comercializavel=True,
        bloqueado_ate=None,
        fonte_dados="steam",
        metadados_origem={},
    )

    return ItemInventarioSteamDTO(
        catalogo=catalogo,
        instancia=instancia,
    )

def criar_inventario_bruto() -> InventarioSteamBruto:
    """Cria um inventário bruto para testes."""
    return InventarioSteamBruto(
        steam_id=STEAM_ID_TESTE,
        app_id=730,
        contexto_id=2,
        total_informado=1,
        ativos=(),
        descricoes=(),
    )

@patch(
    "skinexa.services.inventory.service."
    "contar_instancias_ativas_usuario",
    return_value=1,
)
@patch(
    "skinexa.services.inventory.service."
    "salvar_instancia_item",
    return_value=20,
)
@patch(
    "skinexa.services.inventory.service."
    "salvar_item_catalogo",
    return_value=10,
)
@patch(
    "skinexa.services.inventory.service."
    "desativar_instancias_usuario",
)
@patch(
    "skinexa.services.inventory.service."
    "normalizar_inventario_steam",
)
@patch(
    "skinexa.services.inventory.service."
    "buscar_inventario_publico",
)
@patch(
    "skinexa.services.inventory.service.engine.begin",
)
 
def test_sincronizar_inventario(
    mock_begin,
    mock_buscar,
    mock_normalizar,
    mock_desativar,
    mock_salvar_catalogo,
    mock_salvar_instancia,
    mock_contar_ativos,
):
    """ Testa a função de sincronização do inventário."""
    conexao = MagicMock()

    mock_begin.return_value = nullcontext(conexao)
    mock_buscar.return_value = criar_inventario_bruto()
    mock_normalizar.return_value = (
        criar_item_normalizado(),
    )

    resultado = InventarioService.sincronizar_inventario(
        usuario_id=1,
        steam_id=STEAM_ID_TESTE,
    )

    assert resultado.usuario_id == 1
    assert resultado.total_informado_steam == 1
    assert resultado.itens_processados == 1
    assert resultado.itens_ativos == 1

    mock_buscar.assert_called_once_with(
        STEAM_ID_TESTE
    )

    mock_normalizar.assert_called_once()

    mock_desativar.assert_called_once_with(
        conexao,
        1,
    )

    mock_salvar_catalogo.assert_called_once()

    mock_salvar_instancia.assert_called_once_with(
        conexao,
        usuario_id=1,
        item_catalogo_id=10,
        item=mock_normalizar.return_value[0].instancia,
    )

    mock_contar_ativos.assert_called_once_with(
        conexao,
        1,
    )  

@patch(
    "skinexa.services.inventory.service."
    "normalizar_inventario_steam",
)
@patch(
    "skinexa.services.inventory.service."
    "buscar_inventario_publico",
)
@patch(
    "skinexa.services.inventory.service.engine.begin",
)

def test_rejeitar_item_de_outro_usuario(
    mock_begin,
    mock_buscar,
    mock_normalizar,
): 
    """Testa se a função de sincronização rejeita itens que não pertencem ao usuário."""
    conexao = MagicMock()

    mock_begin.return_value = nullcontext(conexao)
    mock_buscar.return_value = criar_inventario_bruto()

    item = criar_item_normalizado()

    instancia_invalida = InstanciaItemSteamDTO(
        steam_id_usuario="76561198000000002",
        app_id=item.instancia.app_id,
        contexto_id=item.instancia.contexto_id,
        asset_id=item.instancia.asset_id,
        class_id=item.instancia.class_id,
        instance_id=item.instancia.instance_id,
        quantidade=item.instancia.quantidade,
        indice_definicao=None,
        indice_pintura=None,
        semente_pintura=None,
        valor_float=None,
        nome_personalizado=None,
        link_inspecao=None,
        stattrak=False,
        contador_stattrak=None,
        souvenir=False,
        trocavel=True,
        comercializavel=True,
        bloqueado_ate=None,
        fonte_dados="steam",
        metadados_origem={},
    )

    mock_normalizar.return_value = (
        ItemInventarioSteamDTO(
            catalogo=item.catalogo,
            instancia=instancia_invalida,
        ),
    )

    with pytest.raises(ValueError):
        InventarioService.sincronizar_inventario(
            usuario_id=1,
            steam_id=STEAM_ID_TESTE,
        )