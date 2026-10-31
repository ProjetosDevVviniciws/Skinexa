"""Analisa caixas e kits musicais sem identidade comercial."""

from skinexa.integrations.catalogo.csgo_api_client import (
    buscar_itens_csgo_api,
)

CATEGORIAS = (
    "caixas",
    "musicas",
)

def sem_identidade_comercial(registro: dict) -> bool:
    """Identifica registros sem nome comercial válido."""

    nome = registro.get("market_hash_name")

    return not (
        isinstance(nome, str)
        and nome.strip()
    )

def resumir_campo(valor: object) -> object:
    """Resume listas e textos extensos para auditoria."""

    if isinstance(valor, list):
        return f"Lista com {len(valor)} elementos"

    if isinstance(valor, dict):
        return f"Dicionario com {len(valor)} campos"

    if isinstance(valor, str):
        return valor[:200]

    return valor

def main() -> int:
    """Examina atributos específicos sem alterar o banco."""

    print("\nSKINEXA - AUDITORIA DE CAIXAS E MUSICAS")
    print("=" * 50)

    total_pendentes = 0

    for categoria in CATEGORIAS:
        registros = buscar_itens_csgo_api(categoria)

        pendentes = [
            registro
            for registro in registros
            if sem_identidade_comercial(registro)
        ]

        total_pendentes += len(pendentes)

        print(f"\nCATEGORIA: {categoria.upper()}")
        print("-" * 50)

        print(f"Registros pendentes: {len(pendentes)}")

        for registro in pendentes:
            campos = {
                "id": registro.get("id"),
                "name": registro.get("name"),
                "def_index": registro.get("def_index"),
                "type": registro.get("type"),
                "description": resumir_campo(
                    registro.get("description")
                ),
            }

            if categoria == "caixas":
                campos.update(
                    {
                        "first_sale_date": registro.get(
                            "first_sale_date"
                        ),
                        "contains": resumir_campo(
                            registro.get("contains")
                        ),
                        "contains_rare": resumir_campo(
                            registro.get("contains_rare")
                        ),
                        "loot_list": resumir_campo(
                            registro.get("loot_list")
                        ),
                        "rental": registro.get("rental"),
                    }
                )

            if categoria == "musicas":
                campos.update(
                    {
                        "exclusive": registro.get(
                            "exclusive"
                        ),
                    }
                )

            print(campos)

    print("\nRESULTADO CONSOLIDADO")
    print("-" * 50)

    print(f"Registros pendentes: {total_pendentes}")
    print("Nenhum registro foi gravado no MySQL.")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())