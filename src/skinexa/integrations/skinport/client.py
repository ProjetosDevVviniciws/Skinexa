"""Centraliza a comunicação HTTP com a API da Skinport."""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

import requests
from flask import current_app

from skinexa.dto.skinport.preco import PrecoSkinportDTO

URL_ITENS_SKINPORT = "https://api.skinport.com/v1/items"
APP_ID_CS2 = 730

class ErroSkinport(RuntimeError):
    """Erro genérico durante consultas à Skinport."""

class SkinportIndisponivel(ErroSkinport):
    """A API da Skinport está indisponível."""

class LimiteSkinportExcedido(ErroSkinport):
    """A Skinport limitou temporariamente as requisições."""

class RespostaSkinportInvalida(ErroSkinport):
    """A Skinport retornou uma resposta inválida."""

@dataclass(frozen=True, slots=True)
class ConsultaPrecosSkinport:
    """Resultado consolidado da consulta de preços."""

    moeda: str
    itens: tuple[PrecoSkinportDTO, ...]

def buscar_precos_skinport(
    *,
    moeda: str = "BRL",
) -> ConsultaPrecosSkinport:
    """Consulta os preços públicos de itens do CS2 na Skinport."""

    moeda_normalizada = moeda.strip().upper()

    if len(moeda_normalizada) != 3:
        raise ValueError(
            "A moeda deve possuir exatamente três caracteres."
        )

    parametros = {
        "app_id": APP_ID_CS2,
        "currency": moeda_normalizada,
    }

    timeout = current_app.config.get(
        "SKINPORT_REQUEST_TIMEOUT",
        10,
    )

    try:
        resposta = requests.get(
            URL_ITENS_SKINPORT,
            params=parametros,
            timeout=timeout,
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "br",
                "User-Agent": "Skinexa/1.0",
            },
        )
    except requests.Timeout as erro:
        raise SkinportIndisponivel(
            "A consulta à Skinport excedeu o tempo limite."
        ) from erro
    except requests.RequestException as erro:
        raise SkinportIndisponivel(
            "Não foi possível consultar a Skinport."
        ) from erro

    if resposta.status_code == 429:
        raise LimiteSkinportExcedido(
            "A Skinport limitou temporariamente as consultas."
        )

    if resposta.status_code >= 500:
        raise SkinportIndisponivel(
            "A API da Skinport está indisponível."
        )

    try:
        resposta.raise_for_status()
        dados = resposta.json()
    except requests.RequestException as erro:
        raise ErroSkinport(
            "A Skinport rejeitou a consulta de preços."
        ) from erro
    except ValueError as erro:
        raise RespostaSkinportInvalida(
            "A Skinport não retornou um JSON válido."
        ) from erro

    itens = _validar_e_criar_dtos(
        dados=dados,
        moeda=moeda_normalizada,
    )

    return ConsultaPrecosSkinport(
        moeda=moeda_normalizada,
        itens=itens,
    )

def _validar_e_criar_dtos(
    *,
    dados: Any,
    moeda: str,
) -> tuple[PrecoSkinportDTO, ...]:
    """Valida a resposta e transforma os itens em DTOs."""

    if not isinstance(dados, list):
        raise RespostaSkinportInvalida(
            "A resposta da Skinport não é uma lista."
        )

    itens: list[PrecoSkinportDTO] = []

    for item in dados:
        if not isinstance(item, dict):
            raise RespostaSkinportInvalida(
                "A resposta contém um item inválido."
            )

        itens.append(
            _criar_dto(
                item=item,
                moeda=moeda,
            )
        )

    return tuple(itens)

def _criar_dto(
    *,
    item: dict[str, Any],
    moeda: str,
) -> PrecoSkinportDTO:
    """Transforma um item bruto da Skinport em DTO."""

    nome_mercado = _obter_texto(
        item.get("market_hash_name")
    )

    if not nome_mercado:
        raise RespostaSkinportInvalida(
            "Um item da Skinport não possui market_hash_name."
        )

    return PrecoSkinportDTO(
        market_hash_name=nome_mercado,
        currency=moeda,
        min_price=_converter_decimal(
            item.get("min_price")
        ),
        max_price=_converter_decimal(
            item.get("max_price")
        ),
        mean_price=_converter_decimal(
            item.get("mean_price")
        ),
        median_price=_converter_decimal(
            item.get("median_price")
        ),
        quantity=_converter_inteiro_opcional(
            item.get("quantity")
        ),
        updated_at=_converter_datetime(
            item.get("updated_at")
        ),
    )

def _converter_decimal(
    valor: Any,
) -> Decimal | None:
    """Converte um valor monetário para Decimal."""

    if valor is None:
        return None

    try:
        return Decimal(str(valor))
    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ) as erro:
        raise RespostaSkinportInvalida(
            "A Skinport retornou um preço inválido."
        ) from erro

def _converter_inteiro_opcional(
    valor: Any,
) -> int | None:
    """Converte um valor opcional para inteiro."""

    if valor is None:
        return None

    try:
        numero = int(valor)
    except (TypeError, ValueError) as erro:
        raise RespostaSkinportInvalida(
            "A Skinport retornou uma quantidade inválida."
        ) from erro

    if numero < 0:
        raise RespostaSkinportInvalida(
            "A Skinport retornou uma quantidade negativa."
        )

    return numero

def _converter_datetime(
    valor: Any,
) -> datetime | None:
    """Converte uma data ISO da Skinport para datetime."""

    if valor is None:
        return None

    if isinstance(valor, bool):
        raise RespostaSkinportInvalida(
            "A Skinport retornou uma data inválida."
        )

    try:
        timestamp = int(valor)

        if timestamp < 0:
            raise ValueError

        return datetime.fromtimestamp(
            timestamp,
            tz=timezone.utc,
        ).replace(
            tzinfo=None,
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
        OSError,
    ) as erro:
        raise RespostaSkinportInvalida(
            "A Skinport retornou uma data inválida."
        ) from erro

def _obter_texto(
    valor: Any,
) -> str | None:
    """Normaliza um valor textual."""

    if valor is None:
        return None

    texto = str(valor).strip()

    return texto or None