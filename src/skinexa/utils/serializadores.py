from datetime import datetime
from decimal import Decimal

def serializar_decimal(
    valor: Decimal | None,
) -> str | None:
    """Converte Decimal para representação JSON segura."""

    if valor is None:
        return None

    return str(valor)

def serializar_datetime(
    valor: datetime | None,
) -> str | None:
    """Converte datetime para ISO 8601."""

    if valor is None:
        return None

    return valor.isoformat()