def normalizar_ordenacao_inventario(
    valor: str | None,
) -> str:
    ordenacoes_permitidas = {
        "nome_asc",
        "nome_desc",
    }

    if valor is None:
        return "nome_asc"

    valor_normalizado = valor.strip()

    if valor_normalizado not in ordenacoes_permitidas:
        return "nome_asc"

    return valor_normalizado