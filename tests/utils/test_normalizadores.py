from skinexa.utils.normalizadores import (
    normalizar_ordenacao_inventario,
)

def test_normalizar_ordenacao_inventario_nome_asc():
    """Testa se o valor nome_asc é normalizado corretamente."""
    resultado = normalizar_ordenacao_inventario(
        "nome_asc"
    )

    assert resultado == "nome_asc"

def test_normalizar_ordenacao_inventario_nome_desc():
    """Testa se o valor nome_desc é normalizado corretamente."""
    resultado = normalizar_ordenacao_inventario(
        "nome_desc"
    )

    assert resultado == "nome_desc"

def test_normalizar_ordenacao_inventario_ausente():
    """Testa se um valor ausente é normalizado para nome_asc."""
    resultado = normalizar_ordenacao_inventario(
        None
    )

    assert resultado == "nome_asc"

def test_normalizar_ordenacao_inventario_vazia():
    """Testa se um valor vazio é normalizado para nome_asc."""
    resultado = normalizar_ordenacao_inventario(
        "   "
    )

    assert resultado == "nome_asc"

def test_normalizar_ordenacao_inventario_invalida():
    """Testa se um valor inválido é normalizado para nome_asc."""
    resultado = normalizar_ordenacao_inventario(
        "preco_desc"
    )

    assert resultado == "nome_asc"