from datetime import datetime

from decimal import Decimal

from skinexa.utils.serializadores import (
    serializar_datetime,
    serializar_decimal,
)

def test_serializar_decimal():
    """Testa a serialização de Decimal para string."""

    resultado = serializar_decimal(
        Decimal("103.16"),
    )

    assert resultado == "103.16"

def test_serializar_decimal_preserva_casas_decimais():
    """Testa se a representação decimal é preservada."""

    resultado = serializar_decimal(
        Decimal("98.40"),
    )

    assert resultado == "98.40"

def test_serializar_decimal_none():
    """Testa a serialização de valor Decimal ausente."""

    resultado = serializar_decimal(None)

    assert resultado is None

def test_serializar_datetime():
    """Testa a serialização de datetime para ISO 8601."""

    valor = datetime(
        2026,
        9,
        19,
        21,
        5,
        30,
    )

    resultado = serializar_datetime(valor)

    assert resultado == "2026-09-19T21:05:30"

def test_serializar_datetime_com_microsegundos():
    """Testa datetime contendo microsegundos."""

    valor = datetime(
        2026,
        9,
        19,
        21,
        5,
        30,
        123456,
    )

    resultado = serializar_datetime(valor)

    assert resultado == (
        "2026-09-19T21:05:30.123456"
    )

def test_serializar_datetime_none():
    """Testa a serialização de datetime ausente."""

    resultado = serializar_datetime(None)

    assert resultado is None