"""Audita grafites da CSGO-API sem identidade comercial."""

from collections import Counter

from skinexa.integrations.catalogo.csgo_api_client import (
    buscar_itens_csgo_api,
)

def possui_identidade_comercial(registro: dict) -> bool:
    """Verifica se o registro possui nome comercial válido."""

    valor = registro.get("market_hash_name")

    return isinstance(valor, str) and bool(valor.strip())

def main() -> int:
    """Analisa os grafites pendentes sem modificar o banco."""

    registros = buscar_itens_csgo_api("grafites")

    pendentes = [
        registro
        for registro in registros
        if not possui_identidade_comercial(registro)
    ]

    comerciais = [
        registro
        for registro in registros
        if possui_identidade_comercial(registro)
    ]

    print("\nSKINEXA - AUDITORIA DE GRAFITES")
    print("=" * 50)

    print(f"Registros recebidos: {len(registros)}")
    print(f"Pendentes: {len(pendentes)}")
    print(f"Com identidade comercial: {len(comerciais)}")

    eventos = Counter()

    for registro in pendentes:
        nome = registro.get("name") or ""

        if " | " in nome:
            partes = nome.split(" | ")

            if len(partes) >= 3:
                evento = partes[-1]
            else:
                evento = "Sem evento identificado"
        else:
            evento = "Sem evento identificado"

        eventos[evento] += 1

    print("\nAGRUPAMENTO POR SUFIXO DO NOME")
    print("-" * 50)

    for evento, quantidade in eventos.most_common(30):
        print(f"{evento}: {quantidade}")

    nomes_comerciais = {
        registro.get("name")
        for registro in comerciais
    }

    correspondencias = [
        registro
        for registro in pendentes
        if registro.get("name") in nomes_comerciais
    ]

    print("\nCORRESPONDENCIAS NOMINAIS")
    print("-" * 50)
    print(
        "Pendentes com nome igual a registro comercial: "
        f"{len(correspondencias)}"
    )

    print("\nEXEMPLOS PENDENTES")
    print("-" * 50)

    for registro in pendentes[:20]:
        print(
            {
                "id": registro.get("id"),
                "name": registro.get("name"),
                "def_index": registro.get("def_index"),
                "tint": registro.get("tint"),
            }
        )

    print("\nNenhum registro foi gravado no MySQL.")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())