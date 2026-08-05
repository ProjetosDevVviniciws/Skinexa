from urllib.parse import urljoin, urlparse

from flask import (
    abort,
    flash,
    redirect,
    request,
    session,
    Blueprint,
    url_for,
)
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
)

from skinexa.integrations.steam.openid import (
    ErroAutenticacaoSteam,
    gerar_url_autenticacao,
    validar_retorno_openid,
)

from skinexa.integrations.steam.perfil import (
    ErroPerfilSteam,
    buscar_perfil_steam,
)

from skinexa.services.usuarios.service import UsuarioService

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
)

def _url_redirecionamento_segura(url_destino: str) -> bool:
    """Verifica se o redirecionamento permanece no Skinexa."""

    url_base = urlparse(request.host_url)
    url_completa = urlparse(
        urljoin(request.host_url, url_destino)
    )

    return (
        url_completa.scheme in {"http", "https"}
        and url_base.netloc == url_completa.netloc
    )

@auth_bp.get("/steam")
def login():
    """Redireciona o usuário para autenticação na Steam."""

    if current_user.is_authenticated:
        return redirect(url_for("home.index"))

    proxima_url = request.args.get("next")

    if (
        proxima_url
        and _url_redirecionamento_segura(proxima_url)
    ):
        session["url_apos_login"] = proxima_url
    else:
        session.pop("url_apos_login", None)

    return redirect(gerar_url_autenticacao())

@auth_bp.get("/steam/retorno")
def retorno_steam():
    """Valida o retorno da Steam e inicia a sessão local."""

    try:
        parametros_openid = {
            chave: valor
            for chave, valor in request.args.items()
            if chave.startswith("openid.")
        }

        steam_id = validar_retorno_openid(
            parametros_openid
        )

        perfil = buscar_perfil_steam(steam_id)

        if perfil is None:
            nome_exibicao = f"Usuario Steam {steam_id[-6:]}"
            url_avatar = None
            url_perfil = (
                f"https://steamcommunity.com/profiles/{steam_id}"
            )
        else:
            nome_exibicao = perfil.nome_exibicao
            url_avatar = perfil.url_avatar
            url_perfil = perfil.url_perfil
        
        usuario = UsuarioService.autenticar_usuario_steam(
                steam_id=steam_id,
                nome_exibicao=nome_exibicao,
                url_avatar=url_avatar,
                url_perfil=url_perfil,
            )

        autenticado = login_user(
            usuario,
            remember=False,
            fresh=True,
        )

        if not autenticado:
            flash(
                "Sua conta não está autorizada a acessar "
                "o Skinexa.",
                "danger",
            )
            return redirect(url_for("home.index"))

        session.permanent = True

        destino = session.pop(
            "url_apos_login",
            url_for("dashboard.index"),
        )

        if not _url_redirecionamento_segura(destino):
            destino = url_for("dashboard.index")

        flash(
            "Autenticação realizada com sucesso.",
            "success",
        )

        return redirect(destino)

    except (
        ErroAutenticacaoSteam,
        ErroPerfilSteam,
        PermissionError,
        RuntimeError,
    ):
        flash(
            "Não foi possível concluir a autenticação "
            "com a Steam.",
            "danger",
        )

        return redirect(url_for("home.index"))

@auth_bp.post("/sair")
@login_required
def logout():
    """Encerra a sessão local do usuário."""

    logout_user()
    session.clear()

    flash(
        "Sua sessão foi encerrada com segurança.",
        "success",
    )

    return redirect(url_for("home.index"))