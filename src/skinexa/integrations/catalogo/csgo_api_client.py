"""Cliente HTTP para os dados públicos da CSGO-API."""

from typing import Any

import requests

URL_BASE_CSGO_API = (
    "https://raw.githubusercontent.com/"
    "ByMykel/CSGO-API/main/public/api/en"
)

ARQUIVOS_CATALOGO = {
    "skins": "skins_not_grouped.json",
    "adesivos": "stickers.json",
    "caixas": "crates.json",
    "agentes": "agents.json",
    "patches": "patches.json",
    "chaveiros": "keychains.json",
    "grafites": "graffiti.json",
    "musicas": "music_kits.json",
    "colecionaveis": "collectibles.json",
}

class ErroCSGOAPI(Exception):
    """Representa uma falha na consulta à CSGO-API."""

def buscar_itens_csgo_api(
    categoria: str,
    *,
    timeout: int = 30,
) -> list[dict[str, Any]]:
    """Consulta os itens de uma categoria da CSGO-API."""

    if categoria not in ARQUIVOS_CATALOGO:
        raise ValueError(
            "Categoria de catálogo não suportada."
        )

    if timeout <= 0:
        raise ValueError(
            "O timeout deve ser maior que zero."
        )

    arquivo = ARQUIVOS_CATALOGO[categoria]

    url = f"{URL_BASE_CSGO_API}/{arquivo}"

    try:
        resposta = requests.get(
            url,
            timeout=timeout,
        )

        resposta.raise_for_status()

        dados = resposta.json()

    except (
        requests.RequestException,
        ValueError,
    ) as erro:
        raise ErroCSGOAPI(
            "Não foi possível consultar a CSGO-API."
        ) from erro

    if not isinstance(dados, list):
        raise ErroCSGOAPI(
            "Formato de resposta inválido da CSGO-API."
        )

    if not all(
        isinstance(item, dict)
        for item in dados
    ):
        raise ErroCSGOAPI(
            "A resposta contém registros inválidos."
        )

    return dados