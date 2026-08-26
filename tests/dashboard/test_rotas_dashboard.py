from datetime import datetime, UTC
from unittest.mock import patch

from skinexa.blueprints.auth.usuario_sessao import UsuarioSessao

from unittest.mock import patch

from skinexa.services.inventory.service import (
    ResultadoSincronizacaoInventario,
)

from skinexa.integrations.steam.inventario import (
    InventarioSteamPrivado,
    LimiteSteamExcedido,
)

from unittest.mock import patch

from datetime import UTC, datetime
from decimal import Decimal

from skinexa.dto.steam.inventario import ItemInventarioDTO

from skinexa.exceptions.inventario import (
    CooldownSincronizacaoAtivo,
)

def test_dashboard_bloqueia_usuario_anonimo(client):
    """Testa se a rota /dashboard bloqueia usuários anônimos."""
    resposta = client.get(
        "/dashboard/",
        follow_redirects=False,
    )

    assert resposta.status_code == 302

    assert "/auth/steam" in resposta.headers["Location"]

def test_dashboard_permite_usuario_autenticado(client):
    """Testa se a rota /dashboard permite usuários autenticados."""
    agora = datetime.now(UTC).replace(tzinfo=None)

    usuario = UsuarioSessao(
        id=1,
        steam_id="76561198000000001",
        nome_exibicao="Usuario de Teste",
        url_avatar=None,
        url_perfil=None,
        status_conta="ativa",
        criado_em=agora,
        atualizado_em=agora,
        ultimo_login_em=agora,
    )

    with patch(
        "skinexa.core.autenticacao."
        "UsuarioService.obter_usuario_sessao",
        return_value=usuario,
    ):
        with client.session_transaction() as sessao:
            sessao["_user_id"] = "1"
            sessao["_fresh"] = True

        resposta = client.get("/dashboard/")

    assert resposta.status_code == 200
    assert b"Dashboard" in resposta.data
    assert b"Usuario de Teste" in resposta.data
    
def criar_usuario_teste() -> UsuarioSessao:
    """Cria um objeto UsuarioSessao para testes."""
    agora = datetime.now(UTC).replace(tzinfo=None)

    return UsuarioSessao(
        id=1,
        steam_id="76561198000000001",
        nome_exibicao="Usuario de Teste",
        url_avatar=None,
        url_perfil=None,
        status_conta="ativa",
        criado_em=agora,
        atualizado_em=agora,
        ultimo_login_em=agora,
    )

def autenticar_cliente(client) -> None:
    """Autentica o cliente de teste como um usuário válido."""
    with client.session_transaction() as sessao:
        sessao["_user_id"] = "1"
        sessao["_fresh"] = True
        
@patch(
    "skinexa.core.autenticacao."
    "UsuarioService.obter_usuario_sessao",
)
@patch(
    "skinexa.blueprints.dashboard.routes."
    "InventarioService.sincronizar_inventario",
)

def test_sincronizar_inventario_com_sucesso(
    mock_sincronizar,
    mock_carregar_usuario,
    client,
):
    """Testa se a rota /dashboard/sincronizar-inventario sincroniza o inventário com sucesso e exibe a mensagem correta."""
    usuario = criar_usuario_teste()

    mock_carregar_usuario.return_value = usuario

    mock_sincronizar.return_value = (
        ResultadoSincronizacaoInventario(
            usuario_id=1,
            total_informado_steam=5,
            itens_processados=5,
            itens_ativos=5,
        )
    )

    autenticar_cliente(client)

    resposta = client.post(
        "/dashboard/sincronizar-inventario"
    )

    assert resposta.status_code == 200
    assert resposta.is_json

    dados = resposta.get_json()

    assert dados["sucesso"] is True
    assert dados["itens_ativos"] == 5
    assert dados["itens_processados"] == 5

    assert (
        dados["mensagem"]
        == "Inventário sincronizado com sucesso."
    )

    mock_sincronizar.assert_called_once_with(
        usuario_id=1,
        steam_id="76561198000000001",
    )

@patch(
    "skinexa.core.autenticacao."
    "UsuarioService.obter_usuario_sessao",
)
@patch(
    "skinexa.blueprints.dashboard.routes."
    "InventarioService.sincronizar_inventario",
)
def test_sincronizar_inventario_privado(
    mock_sincronizar,
    mock_carregar_usuario,
    client,
):
    mock_carregar_usuario.return_value = (
        criar_usuario_teste()
    )

    mock_sincronizar.side_effect = (
        InventarioSteamPrivado(
            "Inventário privado."
        )
    )

    autenticar_cliente(client)

    resposta = client.post(
        "/dashboard/sincronizar-inventario"
    )

    assert resposta.status_code == 403
    assert resposta.is_json

    dados = resposta.get_json()

    assert dados["sucesso"] is False

    assert (
        "inventário da Steam está privado"
        in dados["mensagem"]
    )
 
def test_sincronizacao_bloqueia_usuario_anonimo(
    client,
):
    """Testa se a rota /dashboard/sincronizar-inventario bloqueia usuários anônimos."""
    resposta = client.post(
        "/dashboard/sincronizar-inventario",
        follow_redirects=False,
    )

    assert resposta.status_code == 302
    assert "/auth/steam" in resposta.headers["Location"]

@patch(
    "skinexa.core.autenticacao."
    "UsuarioService.obter_usuario_sessao",
) 

def test_dashboard_renderiza_sem_buscar_inventario(
    mock_carregar_usuario,
    client,
):
    """Testa se a rota /dashboard renderiza a página sem buscar o inventário do usuário."""
    usuario = criar_usuario_teste()

    mock_carregar_usuario.return_value = usuario

    autenticar_cliente(client)

    with patch(
        "skinexa.blueprints.dashboard.routes."
        "InventarioService.listar_inventario"
    ) as mock_listar:
        resposta = client.get(
            "/dashboard/"
        )

    assert resposta.status_code == 200

    conteudo = resposta.get_data(
        as_text=True
    )

    assert "Dashboard" in conteudo
    assert "Carregando inventário" in conteudo

    mock_listar.assert_not_called()

def criar_item_inventario_teste() -> ItemInventarioDTO:
    """Cria um objeto ItemInventarioDTO para testes."""
    agora = datetime.now(
        UTC
    ).replace(tzinfo=None)

    return ItemInventarioDTO(
        instancia_id=1,
        item_catalogo_id=10,
        asset_id="1001",
        nome_mercado=(
            "AK-47 | Redline (Field-Tested)"
        ),
        nome_exibicao="AK-47 | Redline",
        tipo_item="Rifle",
        nome_arma="AK-47",
        nome_acabamento="Redline",
        estado_exterior="Field-Tested",
        raridade="Classified",
        qualidade=None,
        colecao="The Phoenix Collection",
        url_icone="https://example.com/item.png",
        url_icone_grande=None,
        valor_float=None,
        stattrak=False,
        souvenir=False,
        trocavel=True,
        comercializavel=True,
        quantidade=1,
        bloqueado_ate=None,
        ultima_visualizacao_em=agora,
    )
    
@patch(
    "skinexa.core.autenticacao."
    "UsuarioService.obter_usuario_sessao",
)
@patch(
    "skinexa.blueprints.dashboard.routes."
    "InventarioService.listar_inventario",
)

def test_obter_inventario_retorna_json(
    mock_listar_inventario,
    mock_carregar_usuario,
    client,
):
    """Testa se a rota /dashboard/inventario retorna os itens do inventário em formato JSON."""
    usuario = criar_usuario_teste()

    mock_carregar_usuario.return_value = usuario

    mock_listar_inventario.return_value = (
        [criar_item_inventario_teste()],
        1,
    )

    autenticar_cliente(client)

    resposta = client.get(
        "/dashboard/inventario?pagina=1"
    )

    assert resposta.status_code == 200
    assert resposta.is_json

    dados = resposta.get_json()

    assert dados["total_itens"] == 1
    assert dados["pagina"] == 1
    assert dados["itens_por_pagina"] == 20
    assert dados["tem_anterior"] is False
    assert dados["tem_proxima"] is False

    assert len(dados["itens"]) == 1

    item = dados["itens"][0]

    assert item["nome_mercado"] == (
        "AK-47 | Redline (Field-Tested)"
    )

    assert item["raridade"] == "Classified"
    assert item["trocavel"] is True
    assert item["comercializavel"] is True

    mock_listar_inventario.assert_called_once_with(
        usuario_id=1,
        pagina=1,
        itens_por_pagina=20,
        busca=None,
        tipo_item=None,
        raridade=None,
        estado_exterior=None,
        stattrak=None,
        souvenir=None,
    )
    
@patch(
    "skinexa.core.autenticacao."
    "UsuarioService.obter_usuario_sessao",
)
@patch(
    "skinexa.blueprints.dashboard.routes."
    "InventarioService.listar_inventario",
)

def test_obter_segunda_pagina_inventario(
    mock_listar_inventario,
    mock_carregar_usuario,
    client,
):
    """Testa se a rota /dashboard/inventario retorna a segunda página do inventário corretamente."""
    mock_carregar_usuario.return_value = (
        criar_usuario_teste()
    )

    mock_listar_inventario.return_value = (
        [criar_item_inventario_teste()],
        45,
    )

    autenticar_cliente(client)

    resposta = client.get(
        "/dashboard/inventario?pagina=2"
    )

    dados = resposta.get_json()

    assert resposta.status_code == 200

    assert dados["pagina"] == 2
    assert dados["tem_anterior"] is True
    assert dados["tem_proxima"] is True

    mock_listar_inventario.assert_called_once_with(
        usuario_id=1,
        pagina=2,
        itens_por_pagina=20,
        busca=None,
        tipo_item=None,
        raridade=None,
        estado_exterior=None,
        stattrak=None,
        souvenir=None,
    )
    
def test_inventario_bloqueia_usuario_anonimo(
    client,
):
    """Testa se a rota /dashboard/inventario bloqueia usuários anônimos."""
    resposta = client.get(
        "/dashboard/inventario",
        follow_redirects=False,
    )

    assert resposta.status_code == 302

    assert "/auth/steam" in (
        resposta.headers["Location"]
    )
    
@patch(
    "skinexa.core.autenticacao."
    "UsuarioService.obter_usuario_sessao",
)
@patch(
    "skinexa.blueprints.dashboard.routes."
    "InventarioService.sincronizar_inventario",
)

def test_sincronizar_inventario_com_limite_steam(
    mock_sincronizar,
    mock_carregar_usuario,
    client,
):
    """"Testa se a rota /dashboard/sincronizar-inventario retorna o status correto quando o limite da Steam é excedido."""
    mock_carregar_usuario.return_value = (
        criar_usuario_teste()
    )

    mock_sincronizar.side_effect = (
        LimiteSteamExcedido(
            "Rate limit."
        )
    )

    autenticar_cliente(client)

    resposta = client.post(
        "/dashboard/sincronizar-inventario"
    )

    assert resposta.status_code == 429

    dados = resposta.get_json()

    assert dados["sucesso"] is False
    
@patch(
    "skinexa.core.autenticacao."
    "UsuarioService.obter_usuario_sessao",
)
@patch(
    "skinexa.blueprints.dashboard.routes."
    "InventarioService.sincronizar_inventario",
)

def test_sincronizar_inventario_com_cooldown(
    mock_sincronizar,
    mock_carregar_usuario,
    client,
):
    """Testa se a rota /dashboard/sincronizar-inventario retorna 429 quando o cooldown ainda está ativo."""

    mock_carregar_usuario.return_value = (
        criar_usuario_teste()
    )

    mock_sincronizar.side_effect = (
        CooldownSincronizacaoAtivo(
            segundos_restantes=75
        )
    )

    autenticar_cliente(client)

    resposta = client.post(
        "/dashboard/sincronizar-inventario"
    )

    assert resposta.status_code == 429
    assert resposta.is_json

    dados = resposta.get_json()

    assert dados["sucesso"] is False

    assert (
        dados["mensagem"]
        == "Aguarde antes de sincronizar novamente."
    )

    assert dados["segundos_restantes"] == 75
    
@patch(
    "skinexa.core.autenticacao."
    "UsuarioService.obter_usuario_sessao",
)
@patch(
    "skinexa.blueprints.dashboard.routes."
    "InventarioService.listar_inventario",
)

def test_obter_inventario_com_busca(
    mock_listar_inventario,
    mock_carregar_usuario,
    client,
):
    """Testa se a rota /dashboard/inventario retorna os itens do inventário filtrados pela busca corretamente."""

    mock_carregar_usuario.return_value = (
        criar_usuario_teste()
    )

    mock_listar_inventario.return_value = (
        [criar_item_inventario_teste()],
        1,
    )

    autenticar_cliente(client)

    resposta = client.get(
        "/dashboard/inventario"
        "?pagina=1&busca=AWP"
    )

    assert resposta.status_code == 200
    assert resposta.is_json

    dados = resposta.get_json()

    assert dados["busca"] == "AWP"
    assert dados["pagina"] == 1
    assert dados["total_itens"] == 1

    mock_listar_inventario.assert_called_once_with(
        usuario_id=1,
        pagina=1,
        itens_por_pagina=20,
        busca="AWP",
        tipo_item=None,
        raridade=None,
        estado_exterior=None,
        stattrak=None,
        souvenir=None,
    )
    
@patch(
    "skinexa.core.autenticacao."
    "UsuarioService.obter_usuario_sessao",
)
@patch(
    "skinexa.blueprints.dashboard.routes."
    "InventarioService.listar_inventario",
)

def test_obter_inventario_busca_sem_resultados(
    mock_listar_inventario,
    mock_carregar_usuario,
    client,
):
    """Testa se a rota /dashboard/inventario retorna corretamente quando a busca não encontra resultados."""

    mock_carregar_usuario.return_value = (
        criar_usuario_teste()
    )

    mock_listar_inventario.return_value = (
        [],
        0,
    )

    autenticar_cliente(client)

    resposta = client.get(
        "/dashboard/inventario"
        "?pagina=1"
        "&busca=xyznaoexiste123"
    )

    assert resposta.status_code == 200

    dados = resposta.get_json()

    assert dados["busca"] == (
        "xyznaoexiste123"
    )

    assert dados["itens"] == []
    assert dados["total_itens"] == 0
    assert dados["tem_anterior"] is False
    assert dados["tem_proxima"] is False

    mock_listar_inventario.assert_called_once_with(
        usuario_id=1,
        pagina=1,
        itens_por_pagina=20,
        busca="xyznaoexiste123",
        tipo_item=None,
        raridade=None,
        estado_exterior=None,
        stattrak=None,
        souvenir=None,
    )
    
@patch(
    "skinexa.core.autenticacao."
    "UsuarioService.obter_usuario_sessao",
)
@patch(
    "skinexa.blueprints.dashboard.routes."
    "InventarioService.listar_inventario",
)

def test_obter_inventario_paginado_com_busca(
    mock_listar_inventario,
    mock_carregar_usuario,
    client,
):
    """Testa se a rota /dashboard/inventario retorna corretamente a segunda página do inventário filtrada pela busca."""

    mock_carregar_usuario.return_value = (
        criar_usuario_teste()
    )

    mock_listar_inventario.return_value = (
        [criar_item_inventario_teste()],
        45,
    )

    autenticar_cliente(client)

    resposta = client.get(
        "/dashboard/inventario"
        "?pagina=2&busca=AWP"
    )

    assert resposta.status_code == 200

    dados = resposta.get_json()

    assert dados["pagina"] == 2
    assert dados["busca"] == "AWP"

    assert dados["tem_anterior"] is True
    assert dados["tem_proxima"] is True

    mock_listar_inventario.assert_called_once_with(
        usuario_id=1,
        pagina=2,
        itens_por_pagina=20,
        busca="AWP",
        tipo_item=None,
        raridade=None,
        estado_exterior=None,
        stattrak=None,
        souvenir=None,
    )
    
@patch(
    "skinexa.core.autenticacao."
    "UsuarioService.obter_usuario_sessao",
)
@patch(
    "skinexa.blueprints.dashboard.routes."
    "InventarioService.listar_inventario",
)

def test_obter_inventario_com_tipo(
    mock_listar_inventario,
    mock_carregar_usuario,
    client,
):
    """Testa se a rota /dashboard/inventario retorna corretamente a primeira página do inventário utilizando filtro por tipo."""

    mock_carregar_usuario.return_value = (
        criar_usuario_teste()
    )

    mock_listar_inventario.return_value = (
        [criar_item_inventario_teste()],
        3,
    )

    autenticar_cliente(client)

    resposta = client.get(
        "/dashboard/inventario"
        "?pagina=1&tipo=Rifle%20de%20Precisão"
    )

    assert resposta.status_code == 200

    dados = resposta.get_json()

    assert dados["tipo"] == "Rifle de Precisão"
    assert dados["total_itens"] == 3

    mock_listar_inventario.assert_called_once_with(
        usuario_id=1,
        pagina=1,
        itens_por_pagina=20,
        busca=None,
        tipo_item="Rifle de Precisão",
        raridade=None,
        estado_exterior=None,
        stattrak=None,
        souvenir=None,
    )
    
@patch(
    "skinexa.core.autenticacao."
    "UsuarioService.obter_usuario_sessao",
)
@patch(
    "skinexa.blueprints.dashboard.routes."
    "InventarioService.listar_inventario",
)

def test_obter_inventario_com_busca_e_tipo(
    mock_listar_inventario,
    mock_carregar_usuario,
    client,
):
    """Testa se a rota /dashboard/inventario retorna corretamente a primeira página do inventário utilizando pesquisa e filtro por tipo na mesma consulta."""

    mock_carregar_usuario.return_value = (
        criar_usuario_teste()
    )

    mock_listar_inventario.return_value = (
        [criar_item_inventario_teste()],
        2,
    )

    autenticar_cliente(client)

    resposta = client.get(
        "/dashboard/inventario"
        "?pagina=1"
        "&busca=AWP"
        "&tipo=Rifle%20de%20Precisão"
    )

    assert resposta.status_code == 200

    dados = resposta.get_json()

    assert dados["busca"] == "AWP"
    assert dados["tipo"] == "Rifle de Precisão"
    assert dados["total_itens"] == 2

    mock_listar_inventario.assert_called_once_with(
        usuario_id=1,
        pagina=1,
        itens_por_pagina=20,
        busca="AWP",
        tipo_item="Rifle de Precisão",
        raridade=None,
        estado_exterior=None,
        stattrak=None,
        souvenir=None,
    )
    
@patch(
    "skinexa.core.autenticacao."
    "UsuarioService.obter_usuario_sessao",
)
@patch(
    "skinexa.blueprints.dashboard.routes."
    "InventarioService.listar_tipos_inventario",
)

def test_obter_tipos_inventario(
    mock_listar_tipos,
    mock_carregar_usuario,
    client,
):
    """Testa se a rota /dashboard/inventario/tipos retorna corretamente os tipos distintos do inventário."""

    mock_carregar_usuario.return_value = (
        criar_usuario_teste()
    )

    mock_listar_tipos.return_value = [
        "Adesivo",
        "Pistola",
        "Rifle",
        "Rifle de Precisão",
    ]

    autenticar_cliente(client)

    resposta = client.get(
        "/dashboard/inventario/tipos"
    )

    assert resposta.status_code == 200
    assert resposta.is_json

    dados = resposta.get_json()

    assert dados["tipos"] == [
        "Adesivo",
        "Pistola",
        "Rifle",
        "Rifle de Precisão",
    ]

    mock_listar_tipos.assert_called_once_with(
        usuario_id=1,
    )
    
@patch(
    "skinexa.core.autenticacao."
    "UsuarioService.obter_usuario_sessao",
)
@patch(
    "skinexa.blueprints.dashboard.routes."
    "InventarioService.listar_inventario",
)

def test_obter_inventario_com_raridade(
    mock_listar_inventario,
    mock_carregar_usuario,
    client,
):
    """Testa se a rota /dashboard/inventario retorna corretamente a primeira página do inventário utilizando filtro por raridade."""
    mock_carregar_usuario.return_value = (
        criar_usuario_teste()
    )

    mock_listar_inventario.return_value = (
        [criar_item_inventario_teste()],
        1,
    )

    autenticar_cliente(client)

    resposta = client.get(
        "/dashboard/inventario"
        "?pagina=1&raridade=Oculto"
    )

    assert resposta.status_code == 200

    dados = resposta.get_json()

    assert dados["raridade"] == "Oculto"
    assert dados["total_itens"] == 1

    mock_listar_inventario.assert_called_once_with(
        usuario_id=1,
        pagina=1,
        itens_por_pagina=20,
        busca=None,
        tipo_item=None,
        raridade="Oculto",
        estado_exterior=None,
        stattrak=None,
        souvenir=None,
    )
    
@patch(
    "skinexa.core.autenticacao."
    "UsuarioService.obter_usuario_sessao",
)
@patch(
    "skinexa.blueprints.dashboard.routes."
    "InventarioService.listar_inventario",
)

def test_obter_inventario_com_busca_tipo_e_raridade(
    mock_listar_inventario,
    mock_carregar_usuario,
    client,
):
    """Testa se a rota /dashboard/inventario retorna corretamente a primeira página do inventário utilizando busca, filtro por tipo e raridade na mesma consulta."""
    mock_carregar_usuario.return_value = (
        criar_usuario_teste()
    )

    mock_listar_inventario.return_value = (
        [criar_item_inventario_teste()],
        1,
    )

    autenticar_cliente(client)

    resposta = client.get(
        "/dashboard/inventario"
        "?pagina=1"
        "&busca=AWP"
        "&tipo=Rifle%20de%20Precisão"
        "&raridade=Oculto"
    )

    assert resposta.status_code == 200

    dados = resposta.get_json()

    assert dados["busca"] == "AWP"
    assert dados["tipo"] == "Rifle de Precisão"
    assert dados["raridade"] == "Oculto"
    assert dados["total_itens"] == 1

    mock_listar_inventario.assert_called_once_with(
        usuario_id=1,
        pagina=1,
        itens_por_pagina=20,
        busca="AWP",
        tipo_item="Rifle de Precisão",
        raridade="Oculto",
        estado_exterior=None,
        stattrak=None,
        souvenir=None,
    )
    
@patch(
    "skinexa.core.autenticacao."
    "UsuarioService.obter_usuario_sessao",
)
@patch(
    "skinexa.blueprints.dashboard.routes."
    "InventarioService.listar_raridades_inventario",
)
def test_obter_raridades_inventario(
    mock_listar_raridades,
    mock_carregar_usuario,
    client,
):
    """Testa se a rota /dashboard/inventario/raridades retorna corretamente as raridades distintas do inventário."""
    mock_carregar_usuario.return_value = (
        criar_usuario_teste()
    )

    mock_listar_raridades.return_value = [
        "Alta Qualidade",
        "Oculto",
        "Restrito",
        "Secreto",
    ]

    autenticar_cliente(client)

    resposta = client.get(
        "/dashboard/inventario/raridades"
    )

    assert resposta.status_code == 200
    assert resposta.is_json

    dados = resposta.get_json()

    assert dados["raridades"] == [
        "Alta Qualidade",
        "Oculto",
        "Restrito",
        "Secreto",
    ]

    mock_listar_raridades.assert_called_once_with(
        usuario_id=1,
    )
    
@patch(
    "skinexa.core.autenticacao."
    "UsuarioService.obter_usuario_sessao",
)
@patch(
    "skinexa.blueprints.dashboard.routes."
    "InventarioService.listar_inventario",
)

def test_obter_inventario_com_estado(
    mock_listar_inventario,
    mock_carregar_usuario,
    client,
):
    """Testa se a rota /dashboard/inventario retorna corretamente a primeira página do inventário utilizando filtro por estado."""

    mock_carregar_usuario.return_value = (
        criar_usuario_teste()
    )

    mock_listar_inventario.return_value = (
        [criar_item_inventario_teste()],
        5,
    )

    autenticar_cliente(client)

    resposta = client.get(
        "/dashboard/inventario"
        "?pagina=1"
        "&estado=Testada%20em%20Campo"
    )

    assert resposta.status_code == 200

    dados = resposta.get_json()

    assert dados["estado"] == "Testada em Campo"
    assert dados["total_itens"] == 5

    mock_listar_inventario.assert_called_once_with(
        usuario_id=1,
        pagina=1,
        itens_por_pagina=20,
        busca=None,
        tipo_item=None,
        raridade=None,
        estado_exterior="Testada em Campo",
        stattrak=None,
        souvenir=None,
    )
    
@patch(
    "skinexa.core.autenticacao."
    "UsuarioService.obter_usuario_sessao",
)
@patch(
    "skinexa.blueprints.dashboard.routes."
    "InventarioService.listar_inventario",
)

def test_obter_inventario_com_todos_os_filtros(
    mock_listar_inventario,
    mock_carregar_usuario,
    client,
):
    """Testa se a rota /dashboard/inventario retorna corretamente a primeira página do inventário utilizando todos os filtros na mesma consulta."""

    mock_carregar_usuario.return_value = (
        criar_usuario_teste()
    )

    mock_listar_inventario.return_value = (
        [criar_item_inventario_teste()],
        1,
    )

    autenticar_cliente(client)

    resposta = client.get(
        "/dashboard/inventario"
        "?pagina=1"
        "&busca=AWP"
        "&tipo=Rifle%20de%20Precisão"
        "&raridade=Oculto"
        "&estado=Testada%20em%20Campo"
    )

    assert resposta.status_code == 200

    dados = resposta.get_json()

    assert dados["busca"] == "AWP"
    assert dados["tipo"] == "Rifle de Precisão"
    assert dados["raridade"] == "Oculto"
    assert dados["estado"] == "Testada em Campo"
    assert dados["total_itens"] == 1

    mock_listar_inventario.assert_called_once_with(
        usuario_id=1,
        pagina=1,
        itens_por_pagina=20,
        busca="AWP",
        tipo_item="Rifle de Precisão",
        raridade="Oculto",
        estado_exterior="Testada em Campo",
        stattrak=None,
        souvenir=None,
    )
    
@patch(
    "skinexa.core.autenticacao."
    "UsuarioService.obter_usuario_sessao",
)
@patch(
    "skinexa.blueprints.dashboard.routes."
    "InventarioService.listar_estados_inventario",
)

def test_obter_estados_inventario(
    mock_listar_estados,
    mock_carregar_usuario,
    client,
):
    """Testa se a rota /dashboard/inventario/estados retorna corretamente os estados distintos do inventário."""

    mock_carregar_usuario.return_value = (
        criar_usuario_teste()
    )

    mock_listar_estados.return_value = [
        "Não pintado",
        "Nova de Fábrica",
        "Pouco Usada",
        "Testada em Campo",
        "Veterana de Guerra",
    ]

    autenticar_cliente(client)

    resposta = client.get(
        "/dashboard/inventario/estados"
    )

    assert resposta.status_code == 200
    assert resposta.is_json

    dados = resposta.get_json()

    assert dados["estados"] == [
        "Não pintado",
        "Nova de Fábrica",
        "Pouco Usada",
        "Testada em Campo",
        "Veterana de Guerra",
    ]

    mock_listar_estados.assert_called_once_with(
        usuario_id=1,
    )
    
@patch(
    "skinexa.core.autenticacao."
    "UsuarioService.obter_usuario_sessao",
)
@patch(
    "skinexa.blueprints.dashboard.routes."
    "InventarioService.listar_inventario",
)

def test_obter_inventario_com_stattrak(
    mock_listar_inventario,
    mock_carregar_usuario,
    client,
):
    """Testa se a rota /dashboard/inventario aplica corretamente o filtro StatTrak."""
    mock_carregar_usuario.return_value = (
        criar_usuario_teste()
    )

    mock_listar_inventario.return_value = (
        [],
        0,
    )

    autenticar_cliente(client)

    resposta = client.get(
        "/dashboard/inventario"
        "?pagina=1&stattrak=1"
    )

    assert resposta.status_code == 200

    dados = resposta.get_json()

    assert dados["stattrak"] is True
    assert dados["souvenir"] is None

    mock_listar_inventario.assert_called_once_with(
        usuario_id=1,
        pagina=1,
        itens_por_pagina=20,
        busca=None,
        tipo_item=None,
        raridade=None,
        estado_exterior=None,
        stattrak=True,
        souvenir=None,
    )
    
@patch(
    "skinexa.core.autenticacao."
    "UsuarioService.obter_usuario_sessao",
)
@patch(
    "skinexa.blueprints.dashboard.routes."
    "InventarioService.listar_inventario",
)

def test_obter_inventario_com_souvenir(
    mock_listar_inventario,
    mock_carregar_usuario,
    client,
):
    """Testa se a rota /dashboard/inventario aplica corretamente o filtro Souvenir."""
    mock_carregar_usuario.return_value = (
        criar_usuario_teste()
    )

    mock_listar_inventario.return_value = (
        [],
        0,
    )

    autenticar_cliente(client)

    resposta = client.get(
        "/dashboard/inventario"
        "?pagina=1&souvenir=1"
    )

    assert resposta.status_code == 200

    dados = resposta.get_json()

    assert dados["souvenir"] is True
    assert dados["stattrak"] is None
    
@patch(
    "skinexa.core.autenticacao."
    "UsuarioService.obter_usuario_sessao",
)
@patch(
    "skinexa.blueprints.dashboard.routes."
    "InventarioService.listar_inventario",
)

def test_obter_inventario_com_stattrak_false(
    mock_listar_inventario,
    mock_carregar_usuario,
    client,
):
    """Testa se a rota /dashboard/inventario preserva corretamente o filtro StatTrak como falso."""
    mock_carregar_usuario.return_value = (
        criar_usuario_teste()
    )

    mock_listar_inventario.return_value = (
        [],
        35,
    )

    autenticar_cliente(client)

    resposta = client.get(
        "/dashboard/inventario"
        "?pagina=1&stattrak=0"
    )

    assert resposta.status_code == 200

    dados = resposta.get_json()

    assert dados["stattrak"] is False

    mock_listar_inventario.assert_called_once_with(
        usuario_id=1,
        pagina=1,
        itens_por_pagina=20,
        busca=None,
        tipo_item=None,
        raridade=None,
        estado_exterior=None,
        stattrak=False,
        souvenir=None,
    )