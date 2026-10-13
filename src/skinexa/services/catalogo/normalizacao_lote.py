"""Normalização em lote dos itens do catálogo CS2."""

from collections import Counter

from typing import Any

from skinexa.dto.catalogo.normalizacao_lote import (
    ErroItemCatalogoDTO, 
    RelatorioNormalizacaoCatalogoDTO
)

from skinexa.integrations.catalogo.normalizador_csgo_api import (
    ErroNormalizacaoCSGOAPI,
    normalizar_item_skin_csgo_api,
)

from skinexa.integrations.catalogo.normalizador_variantes_csgo_api import (
    normalizar_variante_skin_csgo_api,
)

def normalizar_lote_skins_csgo_api(
    registros: list[dict[str, Any]],
) -> RelatorioNormalizacaoCatalogoDTO:
    """Normaliza registros de skins e remove duplicações comerciais."""

    itens_normalizados = []
    variantes_normalizadas = []
    erros = []

    nomes_encontrados = set()
    variantes_encontradas = set()

    total_duplicados = 0
    total_variantes_duplicadas = 0

    for indice, registro in enumerate(registros):
        identificador_externo = None

        if isinstance(registro, dict):
            identificador = registro.get("id")

            if isinstance(identificador, str):
                identificador_externo = identificador

        try:
            item = normalizar_item_skin_csgo_api(
                registro
            )

            variante = normalizar_variante_skin_csgo_api(
                registro
            )
            
        except ErroNormalizacaoCSGOAPI as erro:
            erros.append(
                ErroItemCatalogoDTO(
                    indice=indice,
                    identificador_externo=identificador_externo,
                    motivo=str(erro),
                )
            )

            continue

        chave_comercial = (
            item.app_id,
            item.nome_mercado,
        )

        if chave_comercial in nomes_encontrados:
            total_duplicados += 1

        else:
            nomes_encontrados.add(
                chave_comercial
            )

            itens_normalizados.append(
                item
            )

        chave_variante = (
            variante.fonte,
            variante.id_externo,
        )

        if chave_variante in variantes_encontradas:
            total_variantes_duplicadas += 1
            
            continue

        variantes_encontradas.add(
            chave_variante
        )

        variantes_normalizadas.append(
            variante
        )
        
    motivos_rejeicao = dict(
        Counter(
            erro.motivo
            for erro in erros
        )
    )

    return RelatorioNormalizacaoCatalogoDTO(
        total_recebidos=len(registros),
        total_normalizados=len(itens_normalizados),
        total_rejeitados=len(erros),
        total_duplicados=total_duplicados,
        itens=tuple(itens_normalizados),
        erros=tuple(erros),
        motivos_rejeicao=motivos_rejeicao,
        total_variantes_normalizadas=len(
            variantes_normalizadas
        ),
        total_variantes_duplicadas=total_variantes_duplicadas,
        variantes=tuple(variantes_normalizadas),
    )