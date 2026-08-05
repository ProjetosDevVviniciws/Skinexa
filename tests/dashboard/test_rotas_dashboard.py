def test_dashboard_bloqueia_usuario_anonimo(client):
    """Testa se a rota /dashboard bloqueia usuários anônimos."""
    resposta = client.get(
        "/dashboard/",
        follow_redirects=False,
    )

    assert resposta.status_code == 302

    assert "/auth/steam" in resposta.headers["Location"]
    
from datetime import datetime, UTC
from unittest.mock import patch

from skinexa.blueprints.auth.usuario_sessao import UsuarioSessao

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