from decimal import Decimal, ROUND_HALF_UP

CASAS_DECIMAIS_MOEDA = Decimal("0.01")

def arredondar_moeda(
    valor: Decimal,
) -> Decimal:
    """Arredonda um valor monetário para duas casas decimais."""

    return valor.quantize(
        CASAS_DECIMAIS_MOEDA,
        rounding=ROUND_HALF_UP,
    )