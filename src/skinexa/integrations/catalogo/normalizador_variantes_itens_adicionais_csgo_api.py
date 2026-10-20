from typing import Any

from skinexa.dto.catalogo.variante import (
    VarianteImportacaoCatalogoDTO,
)

from skinexa.integrations.catalogo.normalizador_itens_adicionais_csgo_api import (
    ErroNormalizacaoItemAdicionalCSGOAPI,
    normalizar_item_adicional_csgo_api,
)

class ErroNormalizacaoVarianteAdicionalCSGOAPI(ValueError):
    """Representa uma falha na normalização de uma variante adicional."""

def normalizar_variante_item_adicional_csgo_api(
    registro: dict[str, Any],
    *,
    categoria: str,
) -> VarianteImportacaoCatalogoDTO:
    """Normaliza o vínculo externo de um item adicional da CSGO-API."""

    try:
        item = normalizar_item_adicional_csgo_api(
            registro,
            categoria=categoria,
        )

    except ErroNormalizacaoItemAdicionalCSGOAPI as erro:
        raise ErroNormalizacaoVarianteAdicionalCSGOAPI(
            str(erro)
        ) from erro

    identificador = registro["id"]
    imagem = registro["image"]
    
    return VarianteImportacaoCatalogoDTO(
        app_id=item.app_id,
        nome_mercado=item.nome_mercado,
        fonte="csgo_api",
        id_externo=identificador,
        url_imagem=imagem,
    )