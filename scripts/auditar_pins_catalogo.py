"""Compara pins comerciais e pendentes da CSGO-API."""

from collections import Counter

from skinexa.integrations.catalogo.csgo_api_client import (
    buscar_itens_csgo_api,
)

def main() -> int:
    """Audita identidade comercial e atributo genuine dos pins."""

    registros = buscar_itens_csgo_api("colecionaveis")

    pins = [
        registro
        for registro in registros
        if registro.get("type") == "Pin"
    ]

    print("\nSKINEXA - AUDITORIA DE PINS")
    print("=" * 50)

    distribuicao = Counter()

    for registro in pins:
        nome_mercado = registro.get("market_hash_name")

        tem_identidade = (
            isinstance(nome_mercado, str)
            and bool(nome_mercado.strip())
        )

        genuine = registro.get("genuine")

        distribuicao[(genuine, tem_identidade)] += 1

    print(f"Total de pins: {len(pins)}")

    print("\nDISTRIBUICAO")
    print("-" * 50)

    for (genuine, tem_identidade), quantidade in sorted(
        distribuicao.items(),
        key=lambda par: str(par[0]),
    ):
        print(
            f"genuine={genuine} | "
            f"identidade_comercial={tem_identidade} | "
            f"total={quantidade}"
        )

    print("\nEXEMPLOS POR GRUPO")
    print("-" * 50)

    for grupo in sorted(distribuicao, key=str):
        genuine, tem_identidade = grupo

        exemplos = [
            registro
            for registro in pins
            if registro.get("genuine") == genuine
            and (
                isinstance(
                    registro.get("market_hash_name"),
                    str,
                )
                and bool(
                    registro["market_hash_name"].strip()
                )
            ) == tem_identidade
        ][:5]

        print(
            f"\ngenuine={genuine} | "
            f"identidade_comercial={tem_identidade}"
        )

        for registro in exemplos:
            print(
                {
                    "id": registro.get("id"),
                    "name": registro.get("name"),
                    "market_hash_name": registro.get(
                        "market_hash_name"
                    ),
                    "def_index": registro.get("def_index"),
                }
            )

    print("\nNenhum registro foi gravado no MySQL.")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())