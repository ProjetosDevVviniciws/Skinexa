import re
from typing import Mapping
from urllib.parse import urlencode

import requests
from flask import current_app

PADRAO_STEAM_ID = re.compile(
    r"^https://steamcommunity\.com/openid/id/(\d{17})$"
)

class ErroAutenticacaoSteam(RuntimeError):
    """Erro durante a validação do OpenID da Steam."""

def gerar_url_autenticacao() -> str:
    """Gera a URL oficial para autenticação OpenID da Steam."""

    url_openid = current_app.config["STEAM_OPENID_URL"]
    realm = current_app.config["STEAM_OPENID_REALM"]
    return_url = current_app.config["STEAM_OPENID_RETURN_URL"]

    if not realm or not return_url:
        raise RuntimeError(
            "As URLs do Steam OpenID não foram configuradas."
        )

    parametros = {
        "openid.ns": "http://specs.openid.net/auth/2.0",
        "openid.mode": "checkid_setup",
        "openid.return_to": return_url,
        "openid.realm": realm,
        "openid.identity": (
            "http://specs.openid.net/auth/2.0/"
            "identifier_select"
        ),
        "openid.claimed_id": (
            "http://specs.openid.net/auth/2.0/"
            "identifier_select"
        ),
    }

    return f"{url_openid}?{urlencode(parametros)}"

def validar_retorno_openid(
    parametros_retorno: Mapping[str, str],
) -> str:
    """
    Valida o retorno OpenID diretamente com a Steam.

    Retorna o SteamID de 64 bits quando o retorno for válido.
    """

    modo = parametros_retorno.get("openid.mode")

    if modo != "id_res":
        raise ErroAutenticacaoSteam(
            "A Steam não confirmou a autenticação."
        )

    claimed_id = parametros_retorno.get("openid.claimed_id")
    identity = parametros_retorno.get("openid.identity")

    if not claimed_id or claimed_id != identity:
        raise ErroAutenticacaoSteam(
            "A identidade retornada pela Steam é inválida."
        )

    correspondencia = PADRAO_STEAM_ID.fullmatch(claimed_id)

    if correspondencia is None:
        raise ErroAutenticacaoSteam(
            "O SteamID retornado possui formato inválido."
        )

    parametros_validacao = dict(parametros_retorno)
    parametros_validacao["openid.mode"] = (
        "check_authentication"
    )

    try:
        resposta = requests.post(
            current_app.config["STEAM_OPENID_URL"],
            data=parametros_validacao,
            timeout=10,
        )
        resposta.raise_for_status()
    except requests.RequestException as erro:
        raise ErroAutenticacaoSteam(
            "Não foi possível validar a autenticação com a Steam."
        ) from erro

    linhas_resposta = {
        chave: valor
        for chave, valor in (
            linha.split(":", 1)
            for linha in resposta.text.splitlines()
            if ":" in linha
        )
    }

    if linhas_resposta.get("is_valid") != "true":
        raise ErroAutenticacaoSteam(
            "A resposta OpenID não foi considerada válida."
        )

    return correspondencia.group(1)