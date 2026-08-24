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

from datetime import UTC, datetime, timedelta

from skinexa.exceptions.inventario import (
    CooldownSincronizacaoAtivo,
)

from skinexa.dto.steam.inventario import ItemInventarioDTO
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
    "atualizar_ultima_sincronizacao_inventario",
    return_value=True,
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
    "skinexa.services.inventory.service."
    "InventarioService.validar_cooldown_sincronizacao",
)
@patch(
    "skinexa.services.inventory.service.engine.connect",
)
@patch(
    "skinexa.services.inventory.service.engine.begin",
)

def test_sincronizar_inventario(
    mock_begin,
    mock_connect,
    mock_validar_cooldown,
    mock_buscar,
    mock_normalizar,
    mock_desativar,
    mock_salvar_catalogo,
    mock_salvar_instancia,
    mock_contar_ativos,
    mock_atualizar_sincronizacao,
):
    """ Testa a função de sincronização do inventário."""
    conexao_cooldown = MagicMock()
    conexao_transacao = MagicMock()

    mock_connect.return_value = nullcontext(
        conexao_cooldown
    )
    mock_begin.return_value = nullcontext(
        conexao_transacao
    )
    
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

    mock_validar_cooldown.assert_called_once_with(
        conexao=conexao_cooldown,
        usuario_id=1,
    )
    
    mock_buscar.assert_called_once_with(
        STEAM_ID_TESTE
    )

    mock_normalizar.assert_called_once()

    mock_desativar.assert_called_once_with(
        conexao_transacao,
        1,
    )

    mock_salvar_catalogo.assert_called_once()

    mock_salvar_instancia.assert_called_once_with(
        conexao_transacao,
        usuario_id=1,
        item_catalogo_id=10,
        item=mock_normalizar.return_value[0].instancia,
    )

    mock_contar_ativos.assert_called_once_with(
        conexao_transacao,
        1,
    )  
    
    mock_atualizar_sincronizacao.assert_called_once_with(
        conexao_transacao,
        1,
    )

@patch(
    "skinexa.services.inventory.service."
    "atualizar_ultima_sincronizacao_inventario",
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
    "skinexa.services.inventory.service."
    "InventarioService.validar_cooldown_sincronizacao",
)
@patch(
    "skinexa.services.inventory.service.engine.connect",
)
@patch(
    "skinexa.services.inventory.service.engine.begin",
)

def test_rejeitar_item_de_outro_usuario(
    mock_begin,
    mock_connect,
    mock_validar_cooldown,
    mock_buscar,
    mock_normalizar,
    mock_atualizar_sincronizacao,
): 
    """Testa se a função de sincronização rejeita itens que não pertencem ao usuário."""

    conexao_cooldown = MagicMock()
    conexao_transacao = MagicMock()

    mock_connect.return_value = nullcontext(
        conexao_cooldown
    )

    mock_begin.return_value = nullcontext(
        conexao_transacao
    )
    
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

    with pytest.raises(
        ValueError,
        match="não pertence ao SteamID",
    ):
        InventarioService.sincronizar_inventario(
            usuario_id=1,
            steam_id=STEAM_ID_TESTE,
        )
        
    mock_validar_cooldown.assert_called_once_with(
        conexao=conexao_cooldown,
        usuario_id=1,
    )
    
    mock_atualizar_sincronizacao.assert_not_called()
        
@patch(
    "skinexa.services.inventory.service."
    "buscar_ultima_sincronizacao_inventario",
    return_value=None,
)

def test_cooldown_permite_primeira_sincronizacao(
    mock_buscar_ultima,
    app,
):
    """Permite sincronização quando o usuário nunca sincronizou."""

    conexao = MagicMock()
    
    with app.app_context():
        app.config[
            "INVENTARIO_COOLDOWN_SEGUNDOS"
        ] = 120

        InventarioService.validar_cooldown_sincronizacao(
            conexao=conexao,
            usuario_id=1,
        )

    mock_buscar_ultima.assert_called_once_with(
        conexao,
        1
    )
    
@patch(
    "skinexa.services.inventory.service."
    "buscar_ultima_sincronizacao_inventario",
)

def test_cooldown_permite_sincronizacao_antiga(
    mock_buscar_ultima,
    app,
):
    """Permite nova sincronização após o cooldown expirar."""

    conexao = MagicMock()
    
    agora = datetime.now(
        UTC
    ).replace(tzinfo=None)

    mock_buscar_ultima.return_value = (
        agora - timedelta(minutes=10)
    )

    with app.app_context():
        app.config[
            "INVENTARIO_COOLDOWN_SEGUNDOS"
        ] = 120

        InventarioService.validar_cooldown_sincronizacao(
            conexao=conexao,
            usuario_id=1,
        )
    
    mock_buscar_ultima.assert_called_once_with(
        conexao,
        1
    )
    
@patch(
    "skinexa.services.inventory.service."
    "buscar_ultima_sincronizacao_inventario",
)

def test_cooldown_bloqueia_sincronizacao_recente(
    mock_buscar_ultima,
    app,
):
    """Bloqueia nova sincronização enquanto o cooldown estiver ativo."""

    conexao = MagicMock()
    
    agora = datetime.now(
        UTC
    ).replace(tzinfo=None)

    mock_buscar_ultima.return_value = (
        agora - timedelta(seconds=30)
    )

    with app.app_context():
        app.config[
            "INVENTARIO_COOLDOWN_SEGUNDOS"
        ] = 120

        with pytest.raises(
            CooldownSincronizacaoAtivo
        ) as erro:
            InventarioService.validar_cooldown_sincronizacao(
                conexao=conexao,
                usuario_id=1
            )

    assert erro.value.segundos_restantes > 0
    assert erro.value.segundos_restantes <= 120
    
    mock_buscar_ultima.assert_called_once_with(
        conexao,
        1
    )

@patch(
    "skinexa.services.inventory.service."
    "buscar_inventario_publico",
)
@patch(
    "skinexa.services.inventory.service."
    "buscar_ultima_sincronizacao_inventario",
)

def test_cooldown_impede_consulta_a_steam(
    mock_buscar_ultima,
    mock_buscar_inventario,
    app,
):
    """Não consulta a Steam quando o cooldown está ativo."""

    agora = datetime.now(
        UTC
    ).replace(tzinfo=None)

    mock_buscar_ultima.return_value = (
        agora - timedelta(seconds=10)
    )

    with app.app_context():
        app.config[
            "INVENTARIO_COOLDOWN_SEGUNDOS"
        ] = 120

        with pytest.raises(
            CooldownSincronizacaoAtivo
        ):
            InventarioService.sincronizar_inventario(
                usuario_id=1,
                steam_id="76561198000000001",
            )

    mock_buscar_inventario.assert_not_called()

@patch(
    "skinexa.services.inventory.service."
    "atualizar_ultima_sincronizacao_inventario",
    return_value=False,
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
    "skinexa.services.inventory.service."
    "InventarioService.validar_cooldown_sincronizacao",
)
@patch(
    "skinexa.services.inventory.service.engine.connect",
)
@patch(
    "skinexa.services.inventory.service.engine.begin",
)

def test_cooldown_falha_ao_atualizar_sincronizacao(
    mock_begin,
    mock_connect,
    mock_validar_cooldown,
    mock_buscar,
    mock_normalizar,
    mock_desativar,
    mock_salvar_catalogo,
    mock_salvar_instancia,
    mock_contar,
    mock_atualizar,
):
    """Testa se a função de sincronização falha quando não consegue atualizar a última sincronização."""

    conexao_cooldown = MagicMock()
    conexao_transacao = MagicMock()

    mock_connect.return_value = nullcontext(
        conexao_cooldown
    )

    mock_begin.return_value = nullcontext(
        conexao_transacao
    )

    mock_buscar.return_value = criar_inventario_bruto()

    mock_normalizar.return_value = (
        criar_item_normalizado(),
    )
    
    with pytest.raises(RuntimeError):
        InventarioService.sincronizar_inventario(
            usuario_id=1,
            steam_id="76561198000000001",
        )

    mock_validar_cooldown.assert_called_once_with(
        conexao=conexao_cooldown,
        usuario_id=1,
    )

    mock_desativar.assert_called_once_with(
        conexao_transacao,
        1,
    )

    mock_salvar_catalogo.assert_called_once()

    mock_salvar_instancia.assert_called_once_with(
        conexao_transacao,
        usuario_id=1,
        item_catalogo_id=10,
        item=mock_normalizar.return_value[0].instancia,
    )

    mock_contar.assert_called_once_with(
        conexao_transacao,
        1,
    )
    
    mock_atualizar.assert_called_once_with(
        conexao_transacao,
        1,
    )
    
def criar_registro_inventario_leitura() -> dict:
    """Cria um registro de inventário para leitura, usado em testes."""
    agora = datetime.now(
        UTC
    ).replace(tzinfo=None)

    return {
        "instancia_id": 1,
        "item_catalogo_id": 10,
        "asset_id": "1001",
        "nome_mercado": (
            "AWP | Printstream (Field-Tested)"
        ),
        "nome_exibicao": "AWP | Cadeia de Caracteres",
        "tipo_item": "Rifle de Precisão",
        "nome_arma": "AWP",
        "nome_acabamento": "Printstream",
        "estado_exterior": "Testada em Campo",
        "raridade": "Oculto",
        "qualidade": None,
        "colecao": None,
        "url_icone": "https://example.com/awp.png",
        "url_icone_grande": None,
        "valor_float": None,
        "stattrak": False,
        "souvenir": False,
        "trocavel": True,
        "comercializavel": True,
        "quantidade": 1,
        "bloqueado_ate": None,
        "ultima_visualizacao_em": agora,
    }
    
@patch(
    "skinexa.services.inventory.service."
    "contar_itens_inventario",
    return_value=1,
)
@patch(
    "skinexa.services.inventory.service."
    "listar_itens_inventario",
)

def test_listar_inventario_com_busca(
    mock_listar,
    mock_contar,
):
    """Testa a função de listar inventário com busca, verificando se os itens retornados correspondem à busca fornecida."""

    mock_listar.return_value = [
        criar_registro_inventario_leitura()
    ]

    itens, total = (
        InventarioService.listar_inventario(
            usuario_id=1,
            pagina=1,
            itens_por_pagina=20,
            busca="AWP",
        )
    )

    assert total == 1
    assert len(itens) == 1

    assert isinstance(
        itens[0],
        ItemInventarioDTO,
    )

    assert itens[0].nome_mercado == (
        "AWP | Printstream (Field-Tested)"
    )

    mock_listar.assert_called_once_with(
        1,
        limite=20,
        deslocamento=0,
        busca="AWP",
        tipo_item=None,
        raridade=None,
        estado_exterior=None,
    )

    mock_contar.assert_called_once_with(
        1,
        busca="AWP",
        tipo_item=None,
        raridade=None,
        estado_exterior=None,
    )
    
@patch(
    "skinexa.services.inventory.service."
    "contar_itens_inventario",
    return_value=1,
)
@patch(
    "skinexa.services.inventory.service."
    "listar_itens_inventario",
)

def test_listar_inventario_normaliza_busca(
    mock_listar,
    mock_contar,
):
    """Testa se a função de listar inventário normaliza a busca, removendo espaços em branco desnecessários."""

    mock_listar.return_value = [
        criar_registro_inventario_leitura()
    ]

    InventarioService.listar_inventario(
        usuario_id=1,
        pagina=1,
        itens_por_pagina=20,
        busca="   AWP   ",
    )

    mock_listar.assert_called_once_with(
        1,
        limite=20,
        deslocamento=0,
        busca="AWP",
        tipo_item=None,
        raridade=None,
        estado_exterior=None,
    )

    mock_contar.assert_called_once_with(
        1,
        busca="AWP",
        tipo_item=None,
        raridade=None,
        estado_exterior=None,
    )
    
@patch(
    "skinexa.services.inventory.service."
    "contar_itens_inventario",
    return_value=0,
)
@patch(
    "skinexa.services.inventory.service."
    "listar_itens_inventario",
    return_value=[],
)
def test_listar_inventario_trata_busca_vazia(
    mock_listar,
    mock_contar,
):
    """Testa se a função de listar inventário trata corretamente uma busca que é apenas espaços em branco, retornando todos os itens do inventário."""

    itens, total = (
        InventarioService.listar_inventario(
            usuario_id=1,
            busca="     ",
        )
    )

    assert itens == []
    assert total == 0

    mock_listar.assert_called_once_with(
        1,
        limite=20,
        deslocamento=0,
        busca=None,
        tipo_item=None,
        raridade=None,
        estado_exterior=None,
    )

    mock_contar.assert_called_once_with(
        1,
        busca=None,
        tipo_item=None,
        raridade=None,
        estado_exterior=None,
    )
    
@patch(
    "skinexa.services.inventory.service."
    "contar_itens_inventario",
    return_value=3,
)
@patch(
    "skinexa.services.inventory.service."
    "listar_itens_inventario",
)

def test_listar_inventario_com_tipo(
    mock_listar,
    mock_contar,
):
    """Testa se a função de listar inventário lista corretamente os itens de acordo com o tipo selecionado."""
    mock_listar.return_value = [
        criar_registro_inventario_leitura()
    ]

    itens, total = InventarioService.listar_inventario(
        usuario_id=1,
        pagina=1,
        itens_por_pagina=20,
        tipo_item="Rifle de Precisão",
    )

    assert total == 3
    assert len(itens) == 1

    mock_listar.assert_called_once_with(
        1,
        limite=20,
        deslocamento=0,
        busca=None,
        tipo_item="Rifle de Precisão",
        raridade=None,
        estado_exterior=None,
    )

    mock_contar.assert_called_once_with(
        1,
        busca=None,
        tipo_item="Rifle de Precisão",
        raridade=None,
        estado_exterior=None,
    )
    
@patch(
    "skinexa.services.inventory.service."
    "contar_itens_inventario",
    return_value=2,
)
@patch(
    "skinexa.services.inventory.service."
    "listar_itens_inventario",
)

def test_listar_inventario_com_busca_e_tipo(
    mock_listar,
    mock_contar,
):
    """Testa se a função de listar inventário combina corretamente a busca e o filtro por tipo."""

    mock_listar.return_value = [
        criar_registro_inventario_leitura()
    ]

    InventarioService.listar_inventario(
        usuario_id=1,
        pagina=1,
        itens_por_pagina=20,
        busca="AWP",
        tipo_item="Rifle de Precisão",
        raridade=None,
        estado_exterior=None,
    )

    mock_listar.assert_called_once_with(
        1,
        limite=20,
        deslocamento=0,
        busca="AWP",
        tipo_item="Rifle de Precisão",
        raridade=None,
        estado_exterior=None,
    )

    mock_contar.assert_called_once_with(
        1,
        busca="AWP",
        tipo_item="Rifle de Precisão",
        raridade=None,
        estado_exterior=None,
    )
    
@patch(
    "skinexa.services.inventory.service."
    "contar_itens_inventario",
    return_value=0,
)
@patch(
    "skinexa.services.inventory.service."
    "listar_itens_inventario",
    return_value=[],
)

def test_listar_inventario_trata_tipo_vazio(
    mock_listar,
    mock_contar,
):
    """Testa se a listagem de inventário trata filtro de tipo vazio como ausência de filtro."""

    InventarioService.listar_inventario(
        usuario_id=1,
        tipo_item="   ",
    )

    mock_listar.assert_called_once_with(
        1,
        limite=20,
        deslocamento=0,
        busca=None,
        tipo_item=None,
        raridade=None,
        estado_exterior=None,
    )

    mock_contar.assert_called_once_with(
        1,
        busca=None,
        tipo_item=None,
        raridade=None,
        estado_exterior=None,
    )
    
@patch(
    "skinexa.services.inventory.service."
    "contar_itens_inventario",
    return_value=1,
)
@patch(
    "skinexa.services.inventory.service."
    "listar_itens_inventario",
)

def test_listar_inventario_com_raridade(
    mock_listar,
    mock_contar,
):
    """Testa se a função de listar inventário lista corretamente os itens de acordo com a raridade selecionado."""
    mock_listar.return_value = [
        criar_registro_inventario_leitura()
    ]

    itens, total = InventarioService.listar_inventario(
        usuario_id=1,
        pagina=1,
        itens_por_pagina=20,
        raridade="Oculto",
    )

    assert total == 1
    assert len(itens) == 1

    mock_listar.assert_called_once_with(
        1,
        limite=20,
        deslocamento=0,
        busca=None,
        tipo_item=None,
        raridade="Oculto",
        estado_exterior=None,
    )

    mock_contar.assert_called_once_with(
        1,
        busca=None,
        tipo_item=None,
        raridade="Oculto",
        estado_exterior=None,
    )

@patch(
    "skinexa.services.inventory.service."
    "contar_itens_inventario",
    return_value=1,
)
@patch(
    "skinexa.services.inventory.service."
    "listar_itens_inventario",
)

def test_listar_inventario_com_busca_tipo_e_raridade(
    mock_listar,
    mock_contar,
):
    """Testa se a função de listar inventário combina corretamente a busca, filtro por tipo e raridade."""
    mock_listar.return_value = [
        criar_registro_inventario_leitura()
    ]

    InventarioService.listar_inventario(
        usuario_id=1,
        pagina=1,
        itens_por_pagina=20,
        busca="AWP",
        tipo_item="Rifle de Precisão",
        raridade="Oculto",
        estado_exterior=None,
    )

    mock_listar.assert_called_once_with(
        1,
        limite=20,
        deslocamento=0,
        busca="AWP",
        tipo_item="Rifle de Precisão",
        raridade="Oculto",
        estado_exterior=None,        
    )

    mock_contar.assert_called_once_with(
        1,
        busca="AWP",
        tipo_item="Rifle de Precisão",
        raridade="Oculto",
        estado_exterior=None,
    )
    
@patch(
    "skinexa.services.inventory.service."
    "contar_itens_inventario",
    return_value=0,
)
@patch(
    "skinexa.services.inventory.service."
    "listar_itens_inventario",
    return_value=[],
)

def test_listar_inventario_trata_raridade_vazia(
    mock_listar,
    mock_contar,
):
    """Testa se a listagem de inventário trata filtro por raridade vazio como ausência de filtro."""
    InventarioService.listar_inventario(
        usuario_id=1,
        raridade="   ",
    )

    mock_listar.assert_called_once_with(
        1,
        limite=20,
        deslocamento=0,
        busca=None,
        tipo_item=None,
        raridade=None,
        estado_exterior=None,
    )

    mock_contar.assert_called_once_with(
        1,
        busca=None,
        tipo_item=None,
        raridade=None,
        estado_exterior=None,
    )
    
@patch(
    "skinexa.services.inventory.service."
    "contar_itens_inventario",
    return_value=5,
)
@patch(
    "skinexa.services.inventory.service."
    "listar_itens_inventario",
)

def test_listar_inventario_com_estado_exterior(
    mock_listar,
    mock_contar,
):
    """Testa se a função de listar inventário lista corretamente os itens de acordo com o estado selecionado."""

    mock_listar.return_value = [
        criar_registro_inventario_leitura()
    ]

    itens, total = (
        InventarioService.listar_inventario(
            usuario_id=1,
            pagina=1,
            itens_por_pagina=20,
            estado_exterior="Testada em Campo",
        )
    )

    assert total == 5
    assert len(itens) == 1

    mock_listar.assert_called_once_with(
        1,
        limite=20,
        deslocamento=0,
        busca=None,
        tipo_item=None,
        raridade=None,
        estado_exterior="Testada em Campo",
    )

    mock_contar.assert_called_once_with(
        1,
        busca=None,
        tipo_item=None,
        raridade=None,
        estado_exterior="Testada em Campo",
    )
    
@patch(
    "skinexa.services.inventory.service."
    "contar_itens_inventario",
    return_value=1,
)
@patch(
    "skinexa.services.inventory.service."
    "listar_itens_inventario",
)

def test_listar_inventario_com_todos_os_filtros(
    mock_listar,
    mock_contar,
):
    """Testa se a função de listar inventário combina corretamente a busca, filtro por tipo, raridade e estador exterior."""

    mock_listar.return_value = [
        criar_registro_inventario_leitura()
    ]

    InventarioService.listar_inventario(
        usuario_id=1,
        pagina=1,
        itens_por_pagina=20,
        busca="AWP",
        tipo_item="Rifle de Precisão",
        raridade="Oculto",
        estado_exterior="Testada em Campo",
    )

    mock_listar.assert_called_once_with(
        1,
        limite=20,
        deslocamento=0,
        busca="AWP",
        tipo_item="Rifle de Precisão",
        raridade="Oculto",
        estado_exterior="Testada em Campo",
    )

    mock_contar.assert_called_once_with(
        1,
        busca="AWP",
        tipo_item="Rifle de Precisão",
        raridade="Oculto",
        estado_exterior="Testada em Campo",
    )
    
@patch(
    "skinexa.services.inventory.service."
    "contar_itens_inventario",
    return_value=0,
)
@patch(
    "skinexa.services.inventory.service."
    "listar_itens_inventario",
    return_value=[],
)

def test_listar_inventario_trata_estado_exterior_vazio(
    mock_listar,
    mock_contar,
):
    """Testa se a listagem de inventário trata filtro por estado vazio como ausência de filtro."""

    InventarioService.listar_inventario(
        usuario_id=1,
        estado_exterior="   ",
    )

    mock_listar.assert_called_once_with(
        1,
        limite=20,
        deslocamento=0,
        busca=None,
        tipo_item=None,
        raridade=None,
        estado_exterior=None,
    )

    mock_contar.assert_called_once_with(
        1,
        busca=None,
        tipo_item=None,
        raridade=None,
        estado_exterior=None,
    )