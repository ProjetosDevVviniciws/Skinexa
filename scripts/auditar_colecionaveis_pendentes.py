"""Audita os colecionáveis sem identidade comercial da CSGO-API."""

from collections import Counter, defaultdict
from typing import Any

from skinexa.integrations.catalogo.csgo_api_client import (
    buscar_itens_csgo_api,
)

def sem_identidade_comercial(registro: dict[str, Any]) -> bool:
    """Verifica a ausência de identidade comercial válida."""

    nome_mercado = registro.get("market_hash_name")

    return not (
        isinstance(nome_mercado, str)
        and nome_mercado.strip()
    )

def auditar_colecionaveis_pendentes() -> int:
    """Agrupa colecionáveis pendentes sem modificar o MySQL."""

    registros = buscar_itens_csgo_api("colecionaveis")

    pendentes = [
        registro
        for registro in registros
        if sem_identidade_comercial(registro)
    ]

    grupos = defaultdict(list)

    for registro in pendentes:
        tipo = registro.get("type") or "Sem tipo"
        grupos[tipo].append(registro)

    print("\nSKINEXA - COLECIONAVEIS PENDENTES")
    print("=" * 50)

    print(f"Registros recebidos: {len(registros)}")
    print(f"Pendentes: {len(pendentes)}")

    for tipo, itens in sorted(grupos.items()):
        print(f"\nTIPO: {tipo.upper()}")
        print("-" * 50)

        print(f"Quantidade: {len(itens)}")

        valores_genuine = Counter(
            str(item.get("genuine"))
            for item in itens
        )

        print(f"Genuine: {dict(valores_genuine)}")

        print("\nEXEMPLOS")

        for item in itens[:5]:
            print(
                {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "type": item.get("type"),
                    "genuine": item.get("genuine"),
                    "premier_season": item.get(
                        "premier_season"
                    ),
                }
            )

    print("\nAUDITORIA CONCLUIDA")
    print("-" * 50)
    print("Nenhum registro foi gravado no MySQL.")

    return 0

if __name__ == "__main__":
    raise SystemExit(
        auditar_colecionaveis_pendentes()
    )