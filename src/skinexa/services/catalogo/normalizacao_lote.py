"""Normalização em lote dos itens do catálogo CS2."""

from collections import Counter

from dataclasses import dataclass

from typing import Any

from skinexa.dto.catalogo.normalizacao_lote import (
    ErroItemCatalogoDTO, 
    RelatorioNormalizacaoCatalogoDTO
)

from skinexa.integrations.catalogo.normalizador_csgo_api import (
    ErroNormalizacaoCSGOAPI,
    normalizar_item_skin_csgo_api,
)

def normalizar_lote_skins_csgo_api(
    registros: list[dict[str, Any]],
) -> RelatorioNormalizacaoCatalogoDTO:
    """Normaliza registros de skins e remove duplicações comerciais."""

    itens_normalizados = []
    erros = []

    nomes_encontrados = set()

    total_duplicados = 0

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

            continue

        nomes_encontrados.add(chave_comercial)

        itens_normalizados.append(item)

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
    )