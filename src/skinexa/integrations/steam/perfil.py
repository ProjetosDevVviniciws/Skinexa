from dataclasses import dataclass

import requests
from flask import current_app

class ErroPerfilSteam(RuntimeError):
    """Erro ao consultar o perfil público da Steam."""

@dataclass(frozen=True, slots=True)
class PerfilSteam:
    steam_id: str
    nome_exibicao: str
    url_avatar: str | None
    url_perfil: str | None

def buscar_perfil_steam(steam_id: str) -> PerfilSteam:
    """Obtém informações públicas básicas do usuário."""

    chave_api = current_app.config.get("STEAM_API_KEY")

    if not chave_api:
        current_app.logger.warning(
            "STEAM_API_KEY não configurada. "
            "O perfil não será enriquecido"
        )
        return None

    url = (
        "https://api.steampowered.com/"
        "ISteamUser/GetPlayerSummaries/v2/"
    )

    parametros = {
        "key": chave_api,
        "steamids": steam_id,
    }

    try:
        resposta = requests.get(
            url,
            params=parametros,
            timeout=10,
        )
        resposta.raise_for_status()
        dados = resposta.json()
        
    except (
        requests.RequestException,
        ValueError,
    ) as erro:
        raise ErroPerfilSteam(
            "Não foi possível consultar o perfil Steam."
        ) from erro

    jogadores = (
        dados.get("response", {})
        .get("players", [])
    )

    if not jogadores:
        raise ErroPerfilSteam(
            "A Steam não retornou o perfil solicitado."
        )

    jogador = jogadores[0]

    steam_id_retornado = str(
        jogador.get("steamid", "")
    )

    if steam_id_retornado != steam_id:
        raise ErroPerfilSteam(
            "O perfil retornado não corresponde ao usuário."
        )

    nome_exibicao = jogador.get("personaname")

    if not nome_exibicao:
        nome_exibicao = f"Usuario Steam {steam_id[-4:]}"

    return PerfilSteam(
        steam_id=steam_id,
        nome_exibicao=nome_exibicao,
        url_avatar=jogador.get("avatarfull"),
        url_perfil=jogador.get("profileurl"),
    )