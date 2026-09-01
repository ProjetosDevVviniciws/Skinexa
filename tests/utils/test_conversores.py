from skinexa.utils.conversores import (
    converter_booleano_query,
)

def test_converter_booleano_query_true():
    """Testa se o valor "1" é convertido corretamente para True."""
    assert converter_booleano_query("1") is True

def test_converter_booleano_query_false():
    """Testa se o valor "0" é convertido corretamente para False."""
    assert converter_booleano_query("0") is False

def test_converter_booleano_query_ausente():
    """Testa se um valor ausente é convertido corretamente para None."""
    assert converter_booleano_query(None) is None

def test_converter_booleano_query_vazio():
    """Testa se o valor vazio é convertido corretamente para None."""
    assert converter_booleano_query("   ") is None

def test_converter_booleano_query_invalido():
    """Testa se o valor inválido é convertido corretamente para None."""
    assert converter_booleano_query("abc") is None