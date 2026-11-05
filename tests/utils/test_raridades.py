import pytest

from skinexa.utils.raridades import obter_cor_raridade

@pytest.mark.parametrize(
    "raridade,cor_esperada",
    [
        ("Consumer Grade", "#B0C3D9"),
        ("Industrial Grade", "#5E98D9"),
        ("Mil-Spec Grade", "#4B69FF"),
        ("Restricted", "#8847FF"),
        ("Classified", "#D32CE6"),
        ("Covert", "#EB4B4B"),
        ("Contraband", "#E4AE39"),
        ("Extraordinary", "#E4AE39"),
        ("High Grade", "#4B69FF"),
        ("Remarkable", "#8847FF"),
        ("Exotic", "#D32CE6"),
        ("Distinguished", "#4B69FF"),
        ("Exceptional", "#8847FF"),
        ("Superior", "#D32CE6"),
        ("Master", "#EB4B4B"),
    ],
)

def test_obter_cor_raridade_conhecida(
    raridade,
    cor_esperada,
):
    """Retorna a cor correspondente a uma raridade conhecida."""

    assert obter_cor_raridade(raridade) == cor_esperada

@pytest.mark.parametrize(
    "raridade",
    [
        None,
        "",
        "Raridade desconhecida",
    ],
)

def test_obter_cor_raridade_desconhecida(raridade):
    """Não atribui cores artificiais a raridades desconhecidas."""

    assert obter_cor_raridade(raridade) is None

def test_obter_cor_raridade_normaliza_texto():
    """Aceita diferenças de caixa e espaços externos."""

    assert obter_cor_raridade("  covert  ") == "#EB4B4B"