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
    )