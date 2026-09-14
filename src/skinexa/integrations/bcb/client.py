"""Centraliza a comunicação HTTP com a API PTAX do Banco Central."""

from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any

import requests
from flask import current_app

from skinexa.dto.cambio.cotacao import (
    CotacaoCambioDTO,
)

URL_PTAX_DOLAR_PERIODO = (
    "https://olinda.bcb.gov.br/"
    "olinda/servico/PTAX/versao/v1/odata/"
    "CotacaoDolarPeriodo(dataInicial=@dataInicial,"
    "dataFinalCotacao=@dataFinalCotacao)"
)

class ErroBCB(RuntimeError):
    """Erro genérico durante consultas ao Banco Central."""

class BCBIndisponivel(ErroBCB):
    """A API do Banco Central está indisponível."""

class RespostaBCBInvalida(ErroBCB):
    """O Banco Central retornou uma resposta inválida."""

class CotacaoBCBNaoEncontrada(ErroBCB):
    """Nenhuma cotação válida foi encontrada."""

def buscar_cotacao_usd_brl() -> CotacaoCambioDTO:
    """Obtém a cotação PTAX USD/BRL de fechamento mais recente."""

    agora = datetime.now()

    data_final = agora.date()
    data_inicial = (
        data_final
        - timedelta(days=7)
    )

    parametros = {
        "@dataInicial": (
            f"'{data_inicial:%m-%d-%Y}'"
        ),
        "@dataFinalCotacao": (
            f"'{data_final:%m-%d-%Y}'"
        ),
        "$format": "json",
    }

    timeout = current_app.config.get(
        "BCB_REQUEST_TIMEOUT",
        10,
    )

    try:
        resposta = requests.get(
            URL_PTAX_DOLAR_PERIODO,
            params=parametros,
            timeout=timeout,
            headers={
                "Accept": "application/json",
                "User-Agent": "Skinexa/1.0",
            },
        )

    except requests.Timeout as erro:
        raise BCBIndisponivel(
            "A consulta ao Banco Central "
            "excedeu o tempo limite."
        ) from erro

    except requests.RequestException as erro:
        raise BCBIndisponivel(
            "Não foi possível consultar "
            "o Banco Central."
        ) from erro

    if resposta.status_code >= 500:
        raise BCBIndisponivel(
            "A API do Banco Central "
            "está indisponível."
        )

    try:
        resposta.raise_for_status()
        dados = resposta.json()

    except requests.RequestException as erro:
        raise ErroBCB(
            "O Banco Central rejeitou "
            "a consulta de câmbio."
        ) from erro

    except ValueError as erro:
        raise RespostaBCBInvalida(
            "O Banco Central não retornou "
            "um JSON válido."
        ) from erro

    return _extrair_cotacao_usd_brl(
        dados
    )

def _extrair_cotacao_usd_brl(
    dados: Any,
) -> CotacaoCambioDTO:
    """Extrai o fechamento USD/BRL mais recente."""

    if not isinstance(dados, dict):
        raise RespostaBCBInvalida(
            "A resposta do Banco Central "
            "não é um objeto JSON."
        )

    valores = dados.get("value")

    if not isinstance(valores, list):
        raise RespostaBCBInvalida(
            "A resposta do Banco Central "
            "não possui uma lista de cotações válida."
        )

    fechamentos = [
        item
        for item in valores
        if (
            isinstance(item, dict)
            and item.get("tipoBoletim")
            == "Fechamento"
        )
    ]

    if not fechamentos:
        raise CotacaoBCBNaoEncontrada(
            "Nenhuma cotação de fechamento "
            "USD/BRL foi encontrada."
        )

    cotacoes = [
        _criar_cotacao(item)
        for item in fechamentos
    ]

    cotacoes_validas = [
        cotacao
        for cotacao in cotacoes
        if cotacao.cotado_em is not None
    ]

    if not cotacoes_validas:
        raise CotacaoBCBNaoEncontrada(
            "Nenhuma cotação USD/BRL "
            "possui data válida."
        )

    return max(
        cotacoes_validas,
        key=lambda cotacao: cotacao.cotado_em,
    )

def _criar_cotacao(
    item: dict[str, Any],
) -> CotacaoCambioDTO:
    """Transforma uma cotação PTAX em DTO interno."""

    taxa = _converter_decimal(
        item.get("cotacaoVenda")
    )

    if taxa <= 0:
        raise RespostaBCBInvalida(
            "O Banco Central retornou "
            "uma cotação inválida."
        )

    return CotacaoCambioDTO(
        moeda_origem="USD",
        moeda_destino="BRL",
        taxa=taxa,
        cotado_em=_converter_datetime(
            item.get("dataHoraCotacao")
        ),
    )

def _converter_decimal(
    valor: Any,
) -> Decimal:
    """Converte um valor de cotação para Decimal."""

    try:
        return Decimal(
            str(valor)
        )

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ) as erro:
        raise RespostaBCBInvalida(
            "O Banco Central retornou "
            "uma cotação inválida."
        ) from erro

def _converter_datetime(
    valor: Any,
) -> datetime | None:
    """Converte a data/hora da cotação PTAX."""

    if valor is None:
        return None

    if not isinstance(valor, str):
        raise RespostaBCBInvalida(
            "O Banco Central retornou "
            "uma data de cotação inválida."
        )

    try:
        return datetime.fromisoformat(
            valor.strip()
        )

    except ValueError as erro:
        raise RespostaBCBInvalida(
            "O Banco Central retornou "
            "uma data de cotação inválida."
        ) from erro