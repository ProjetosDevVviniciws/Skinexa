"""Normalização das variantes fornecidas pela CSGO-API."""

from typing import Any

from skinexa.dto.catalogo.variante import (
    VarianteImportacaoCatalogoDTO,
)

from skinexa.integrations.catalogo.normalizador_csgo_api import (
    ErroNormalizacaoCSGOAPI,
    normalizar_item_skin_csgo_api,
)

FONTE_CSGO_API = "csgo_api"

NOMES_VARIANTES_CSGO_API = {
    "am_ruby_marbleized": "Ruby",
    "am_sapphire_marbleized": "Sapphire",
    "am_blackpearl_marbleized": "Black Pearl",
    "am_doppler_phase1": "Phase 1",
    "am_doppler_phase2": "Phase 2",
    "am_doppler_phase3": "Phase 3",
    "am_doppler_phase4": "Phase 4",
}

def _obter_texto(valor: Any) -> str | None:
    """Obtém um texto não vazio."""

    if not isinstance(valor, str):
        return None

    texto = valor.strip()

    return texto or None

def _obter_identificador_acabamento(
    registro: dict[str, Any],
) -> str | None:
    """Obtém o identificador técnico do acabamento."""

    original = registro.get("original")

    if not isinstance(original, dict):
        return None

    imagem_inventario = _obter_texto(
        original.get("image_inventory")
    )

    if imagem_inventario is None:
        return None

    for identificador in sorted(
        NOMES_VARIANTES_CSGO_API,
        key=len,
        reverse=True,
    ):
        if imagem_inventario.endswith(
            f"_{identificador}_light"
        ):
            return identificador

    return None

def normalizar_variante_skin_csgo_api(
    registro: dict[str, Any],
) -> VarianteImportacaoCatalogoDTO:
    """Normaliza uma variante de skin da CSGO-API."""

    item = normalizar_item_skin_csgo_api(
        registro
    )

    id_externo = _obter_texto(
        registro.get("id")
    )

    if id_externo is None:
        raise ErroNormalizacaoCSGOAPI(
            "Variante sem identificador externo válido."
        )

    if len(id_externo) > 100:
        raise ErroNormalizacaoCSGOAPI(
            "Identificador externo excede 100 caracteres."
        )

    skin_id_externo = _obter_texto(
        registro.get("skin_id")
    )

    if (
        skin_id_externo is not None
        and len(skin_id_externo) > 100
    ):
        raise ErroNormalizacaoCSGOAPI(
            "Skin ID externo excede 100 caracteres."
        )

    identificador_acabamento = (
        _obter_identificador_acabamento(
            registro
        )
    )

    nome_variante = NOMES_VARIANTES_CSGO_API.get(
        identificador_acabamento
    )

    return VarianteImportacaoCatalogoDTO(
        app_id=item.app_id,
        nome_mercado=item.nome_mercado,
        fonte=FONTE_CSGO_API,
        id_externo=id_externo,
        skin_id_externo=skin_id_externo,
        indice_pintura=item.indice_pintura,
        identificador_acabamento=identificador_acabamento,
        nome_variante=nome_variante,
        url_imagem=item.url_icone_grande,
    )