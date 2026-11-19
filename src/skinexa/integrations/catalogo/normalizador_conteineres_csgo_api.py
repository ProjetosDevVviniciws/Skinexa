"""Normalização dos contêineres fornecidos pela CSGO-API."""

from typing import Any

from skinexa.dto.catalogo.conteineres import (
    ConteinerCatalogoDTO,
)

FONTE_CSGO_API = "csgo_api"

class ErroNormalizacaoConteinerCSGOAPI(ValueError):
    """Representa dados inválidos na normalização de contêineres."""

def _obter_texto(
    valor: Any,
) -> str | None:
    """Normaliza um valor textual opcional."""

    if not isinstance(valor, str):
        return None

    texto = valor.strip()

    return texto or None

def normalizar_conteiner_csgo_api(
    registro: dict[str, Any],
) -> ConteinerCatalogoDTO:
    """Normaliza um contêiner fornecido pela CSGO-API."""

    if not isinstance(registro, dict):
        raise ErroNormalizacaoConteinerCSGOAPI(
            "Registro de contêiner inválido."
        )

    id_externo = _obter_texto(
        registro.get("id")
    )

    if id_externo is None:
        raise ErroNormalizacaoConteinerCSGOAPI(
            "Contêiner sem ID externo válido."
        )

    if len(id_externo) > 150:
        raise ErroNormalizacaoConteinerCSGOAPI(
            "ID externo do contêiner excede 150 caracteres."
        )

    nome = _obter_texto(
        registro.get("name")
    )

    if nome is None:
        raise ErroNormalizacaoConteinerCSGOAPI(
            "Contêiner sem nome válido."
        )

    if len(nome) > 255:
        raise ErroNormalizacaoConteinerCSGOAPI(
            "Nome do contêiner excede 255 caracteres."
        )

    tipo_conteiner = _obter_texto(
        registro.get("type")
    )

    if (
        tipo_conteiner is not None
        and len(tipo_conteiner) > 100
    ):
        raise ErroNormalizacaoConteinerCSGOAPI(
            "Tipo do contêiner excede 100 caracteres."
        )

    url_imagem = _obter_texto(
        registro.get("image")
    )

    return ConteinerCatalogoDTO(
        fonte=FONTE_CSGO_API,
        id_externo=id_externo,
        nome=nome,
        item_catalogo_id=None,
        tipo_conteiner=tipo_conteiner,
        url_imagem=url_imagem,
    )