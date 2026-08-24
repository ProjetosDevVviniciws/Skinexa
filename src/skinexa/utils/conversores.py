def converter_booleano_query(
    valor: str | None,
) -> bool | None:
    """
    Converte um parâmetro booleano de query string.

    Valores aceitos:
    - "1": True
    - "0": False
    - ausente ou vazio: None
    """

    if valor is None:
        return None

    valor = valor.strip()

    if not valor:
        return None

    if valor == "1":
        return True

    if valor == "0":
        return False

    return None