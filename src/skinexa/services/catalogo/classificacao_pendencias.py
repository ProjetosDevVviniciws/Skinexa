"""Classifica registros sem identidade comercial da CSGO-API."""

from typing import Any

MOTIVO_SEM_IDENTIDADE = "sem_identidade_comercial"
MOTIVO_NAO_COMERCIALIZAVEL = "nao_comercializavel_fonte"

def classificar_pendencia_catalogo(
    registro: dict[str, Any],
) -> str:
    """Classifica uma pendência a partir dos atributos da fonte."""

    if registro.get("marketable") is False:
        return MOTIVO_NAO_COMERCIALIZAVEL

    return MOTIVO_SEM_IDENTIDADE