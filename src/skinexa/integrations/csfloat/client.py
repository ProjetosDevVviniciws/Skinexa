"""Centraliza a comunicação HTTP com a API da CSFloat."""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import requests
from flask import current_app

from skinexa.dto.csfloat.preco import (
    PrecoCSFloatDTO,
)

URL_LISTINGS_CSFLOAT = (
    "https://csfloat.com/api/v1/listings"
)

LIMITE_MAXIMO_LISTINGS = 50

class ErroCSFloat(RuntimeError):
    """Erro genérico durante consultas à CSFloat."""

class CSFloatIndisponivel(ErroCSFloat):
    """A API da CSFloat está indisponível."""

class LimiteCSFloatExcedido(ErroCSFloat):
    """A CSFloat limitou temporariamente as requisições."""

class AutenticacaoCSFloatInvalida(ErroCSFloat):
    """A CSFloat rejeitou as credenciais utilizadas."""

class RespostaCSFloatInvalida(ErroCSFloat):
    """A CSFloat retornou uma resposta inválida."""

@dataclass(frozen=True, slots=True)
class ConsultaPrecosCSFloat:
    """Resultado consolidado da consulta de preços."""

    nome_mercado: str
    itens: tuple[PrecoCSFloatDTO, ...]

def buscar_precos_csfloat(
    *,
    nome_mercado: str,
    limite: int = LIMITE_MAXIMO_LISTINGS,
) -> ConsultaPrecosCSFloat:
    """
    Consulta anúncios ativos de um item na CSFloat.

    Os resultados são solicitados em ordem crescente
    de preço para facilitar a identificação do menor
    preço disponível.
    """

    nome_normalizado = nome_mercado.strip()

    if not nome_normalizado:
        raise ValueError(
            "O nome de mercado do item é obrigatório."
        )

    if (
        limite < 1
        or limite > LIMITE_MAXIMO_LISTINGS
    ):
        raise ValueError(
            "O limite deve estar entre 1 e 50."
        )

    parametros = {
        "market_hash_name": nome_normalizado,
        "limit": limite,
        "sort_by": "lowest_price",
    }

    timeout = current_app.config.get(
        "CSFLOAT_REQUEST_TIMEOUT",
        10,
    )

    headers = {
        "Accept": "application/json",
        "User-Agent": "Skinexa/1.0",
    }

    chave_api = current_app.config.get(
        "CSFLOAT_API_KEY"
    )

    if chave_api:
        headers["Authorization"] = chave_api

    try:
        resposta = requests.get(
            URL_LISTINGS_CSFLOAT,
            params=parametros,
            timeout=timeout,
            headers=headers,
        )

    except requests.Timeout as erro:
        raise CSFloatIndisponivel(
            "A consulta à CSFloat excedeu "
            "o tempo limite."
        ) from erro

    except requests.RequestException as erro:
        raise CSFloatIndisponivel(
            "Não foi possível consultar a CSFloat."
        ) from erro

    if resposta.status_code == 429:
        raise LimiteCSFloatExcedido(
            "A CSFloat limitou temporariamente "
            "as consultas."
        )

    if resposta.status_code in {
        401,
        403,
    }:
        raise AutenticacaoCSFloatInvalida(
            "A CSFloat rejeitou a autorização "
            "utilizada na consulta."
        )

    if resposta.status_code >= 500:
        raise CSFloatIndisponivel(
            "A API da CSFloat está indisponível."
        )

    try:
        resposta.raise_for_status()
        dados = resposta.json()

    except requests.RequestException as erro:
        raise ErroCSFloat(
            "A CSFloat rejeitou a consulta "
            "de preços."
        ) from erro

    except ValueError as erro:
        raise RespostaCSFloatInvalida(
            "A CSFloat não retornou um JSON válido."
        ) from erro

    itens = _validar_e_criar_dtos(
        dados=dados,
        nome_mercado=nome_normalizado,
    )

    return ConsultaPrecosCSFloat(
        nome_mercado=nome_normalizado,
        itens=itens,
    )

def _validar_e_criar_dtos(
    *,
    dados: Any,
    nome_mercado: str,
) -> tuple[PrecoCSFloatDTO, ...]:
    """Valida a resposta e transforma listings em DTOs."""

    if not isinstance(dados, list):
        raise RespostaCSFloatInvalida(
            "A resposta da CSFloat não é uma lista."
        )

    itens: list[PrecoCSFloatDTO] = []

    for listing in dados:
        if not isinstance(listing, dict):
            raise RespostaCSFloatInvalida(
                "A resposta contém um anúncio inválido."
            )

        dto = _criar_dto(
            listing=listing,
        )

        if dto.market_hash_name != nome_mercado:
            raise RespostaCSFloatInvalida(
                "A CSFloat retornou um item diferente "
                "do item solicitado."
            )

        itens.append(dto)

    return tuple(itens)

def _criar_dto(
    *,
    listing: dict[str, Any],
) -> PrecoCSFloatDTO:
    """Transforma um anúncio bruto da CSFloat em DTO."""

    item = listing.get("item")

    if not isinstance(item, dict):
        raise RespostaCSFloatInvalida(
            "Um anúncio da CSFloat não possui "
            "dados válidos do item."
        )

    nome_mercado = _obter_texto(
        item.get("market_hash_name")
    )

    if not nome_mercado:
        raise RespostaCSFloatInvalida(
            "Um item da CSFloat não possui "
            "market_hash_name."
        )

    return PrecoCSFloatDTO(
        market_hash_name=nome_mercado,
        preco=_converter_preco_centavos(
            listing.get("price")
        ),
        criado_em=_converter_datetime(
            listing.get("created_at")
        ),
    )

def _converter_preco_centavos(
    valor: Any,
) -> Decimal:
    """
    Converte o preço inteiro em centavos da CSFloat
    para Decimal na unidade monetária principal.
    """

    if (
        isinstance(valor, bool)
        or not isinstance(valor, int)
    ):
        raise RespostaCSFloatInvalida(
            "A CSFloat retornou um preço inválido."
        )

    if valor < 0:
        raise RespostaCSFloatInvalida(
            "A CSFloat retornou um preço negativo."
        )

    return (
        Decimal(valor)
        / Decimal("100")
    )

def _converter_datetime(
    valor: Any,
) -> datetime | None:
    """Converte uma data ISO 8601 da CSFloat."""

    if valor is None:
        return None

    if not isinstance(valor, str):
        raise RespostaCSFloatInvalida(
            "A CSFloat retornou uma data inválida."
        )

    texto = valor.strip()

    if not texto:
        raise RespostaCSFloatInvalida(
            "A CSFloat retornou uma data inválida."
        )

    try:
        if texto.endswith("Z"):
            texto = (
                texto[:-1]
                + "+00:00"
            )

        data = datetime.fromisoformat(
            texto
        )

        if data.tzinfo is not None:
            data = (
                data.astimezone(
                    timezone.utc
                )
                .replace(
                    tzinfo=None
                )
            )

        return data

    except ValueError as erro:
        raise RespostaCSFloatInvalida(
            "A CSFloat retornou uma data inválida."
        ) from erro

def _obter_texto(
    valor: Any,
) -> str | None:
    """Normaliza um valor textual."""

    if valor is None:
        return None

    texto = str(valor).strip()

    return texto or None