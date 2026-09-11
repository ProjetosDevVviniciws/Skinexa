from decimal import Decimal

from skinexa.utils.monetario import (
    arredondar_moeda,
)

def test_arredondar_moeda_para_cima():
    """Testa arredondamento monetário para cima."""

    resultado = arredondar_moeda(
        Decimal("10.125")
    )

    assert resultado == Decimal("10.13")

def test_arredondar_moeda_para_baixo():
    """Testa arredondamento monetário para baixo."""

    resultado = arredondar_moeda(
        Decimal("10.124")
    )

    assert resultado == Decimal("10.12")

def test_arredondar_moeda_mantem_duas_casas():
    """Testa valor que já possui duas casas decimais."""

    resultado = arredondar_moeda(
        Decimal("75.18")
    )

    assert resultado == Decimal("75.18")