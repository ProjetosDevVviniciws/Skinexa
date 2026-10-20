"""Normaliza lotes de categorias adicionais da CSGO-API."""

from collections import Counter
from typing import Any

from skinexa.dto.catalogo.normalizacao_itens_adicionais import (
    ErroNormalizacaoItemAdicionalDTO,
    RegistroPendenteCatalogoDTO,
    RelatorioItensAdicionaisDTO,
)

from skinexa.integrations.catalogo.normalizador_itens_adicionais_csgo_api import (
    ErroNormalizacaoItemAdicionalCSGOAPI,
    TIPOS_ITENS_ADICIONAIS,
    normalizar_item_adicional_csgo_api,
)

from skinexa.integrations.catalogo.normalizador_variantes_itens_adicionais_csgo_api import (
    ErroNormalizacaoVarianteAdicionalCSGOAPI,
    normalizar_variante_item_adicional_csgo_api,
)

def normalizar_lote_itens_adicionais_csgo_api(
    registros: list[dict[str, Any]],
    *,
    categoria: str,
) -> RelatorioItensAdicionaisDTO:
    """Normaliza itens adicionais e seus vínculos externos."""

    if categoria not in TIPOS_ITENS_ADICIONAIS:
        raise ValueError(
            f"Categoria não suportada: {categoria}"
        )

    itens = []
    variantes = []
    pendentes = []
    erros = []

    chaves_comerciais = set()
    variantes_encontradas = {}

    total_duplicados = 0
    total_variantes_duplicadas = 0
    
    for indice, registro in enumerate(registros):
        id_externo = None

        if isinstance(registro, dict):
            identificador = registro.get("id")

            if isinstance(identificador, str):
                id_externo = identificador

            nome = registro.get("name")
            imagem = registro.get("image")
            nome_mercado = registro.get("market_hash_name")

            if (
                isinstance(identificador, str)
                and identificador.strip()
                and isinstance(nome, str)
                and nome.strip()
                and isinstance(imagem, str)
                and imagem.strip()
                and (
                    not isinstance(nome_mercado, str)
                    or not nome_mercado.strip()
                )
            ):
                pendentes.append(
                    RegistroPendenteCatalogoDTO(
                        categoria=categoria,
                        indice=indice,
                        id_externo=identificador,
                        nome_exibicao=nome,
                    )
                )

                continue

        try:
            item = normalizar_item_adicional_csgo_api(
                registro,
                categoria=categoria,
            )

            variante = normalizar_variante_item_adicional_csgo_api(
                registro,
                categoria=categoria,
            )
            
        except (
            ErroNormalizacaoItemAdicionalCSGOAPI,
            ErroNormalizacaoVarianteAdicionalCSGOAPI,
        ) as erro:
            erros.append(
                ErroNormalizacaoItemAdicionalDTO(
                    categoria=categoria,
                    indice=indice,
                    id_externo=id_externo,
                    motivo=str(erro),
                )
            )

            continue

        chave_comercial = (
            item.app_id,
            item.nome_mercado,
        )

        chave_variante = (
            variante.fonte,
            variante.id_externo,
        )
        
        if chave_variante in variantes_encontradas:
            chave_anterior = variantes_encontradas[
                chave_variante
            ]

            if chave_anterior != chave_comercial:
                erros.append(
                    ErroNormalizacaoItemAdicionalDTO(
                        categoria=categoria,
                        indice=indice,
                        id_externo=id_externo,
                        motivo=(
                            "ID externo associado a itens "
                            "comerciais diferentes."
                        ),
                    )
                )

                continue

            total_variantes_duplicadas += 1

        else:
            variantes_encontradas[chave_variante] = (
                chave_comercial
            )

            variantes.append(
                variante
            )

        if chave_comercial in chaves_comerciais:
            total_duplicados += 1

        else:
            chaves_comerciais.add(
                chave_comercial
            )

            itens.append(
                item
            )

    motivos_rejeicao = dict(
        Counter(
            erro.motivo
            for erro in erros
        )
    )

    return RelatorioItensAdicionaisDTO(
        categoria=categoria,
        total_recebidos=len(registros),
        total_normalizados=len(itens),
        total_sem_identidade_comercial=len(pendentes),
        total_rejeitados=len(erros),
        total_duplicados=total_duplicados,
        itens=tuple(itens),
        pendentes=tuple(pendentes),
        erros=tuple(erros),
        motivos_rejeicao=motivos_rejeicao,
        total_variantes_normalizadas=len(
            variantes
        ),
        total_variantes_duplicadas=(
            total_variantes_duplicadas
        ),
        variantes=tuple(variantes),
    )