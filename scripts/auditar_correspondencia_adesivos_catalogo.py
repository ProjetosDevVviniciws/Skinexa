"""Audita a correspondência entre adesivos e adesivos encapsulados pendentes."""

from collections import Counter

from skinexa.integrations.catalogo.csgo_api_client import (
    buscar_itens_csgo_api,
)

def obter_pendentes(categoria: str) -> list[dict]:
    """Retorna registros sem identidade comercial válida."""

    registros = buscar_itens_csgo_api(categoria)

    return [
        registro
        for registro in registros
        if not (
            isinstance(registro.get("market_hash_name"), str)
            and registro["market_hash_name"].strip()
        )
    ]

def indexar_por_def_index(
    registros: list[dict],
    categoria: str,
) -> dict[str, dict]:
    """Indexa registros e rejeita identificadores ausentes ou duplicados."""

    indice = {}

    for registro in registros:
        identificador = registro.get("def_index")

        if identificador is None or str(identificador) == "":
            raise RuntimeError(
                f"{categoria}: registro sem def_index."
            )

        chave = str(identificador)

        if chave in indice:
            raise RuntimeError(
                f"{categoria}: def_index duplicado: {chave}"
            )

        indice[chave] = registro

    return indice

def auditar_correspondencia() -> int:
    """Compara os registros pendentes sem alterar o banco."""

    adesivos = indexar_por_def_index(
        obter_pendentes("adesivos"),
        "adesivos",
    )

    encapsulados = indexar_por_def_index(
        obter_pendentes("adesivos_encapsulados"),
        "adesivos_encapsulados",
    )

    chaves_adesivos = set(adesivos)
    chaves_encapsulados = set(encapsulados)

    correspondentes = chaves_adesivos & chaves_encapsulados

    somente_adesivos = chaves_adesivos - chaves_encapsulados
    somente_encapsulados = chaves_encapsulados - chaves_adesivos

    tipos_diferentes = []
    nomes_diferentes = []

    for chave in sorted(correspondentes):
        adesivo = adesivos[chave]
        encapsulado = encapsulados[chave]

        if adesivo.get("type") != encapsulado.get("type"):
            tipos_diferentes.append(chave)

        nome_adesivo = adesivo.get("name", "")
        nome_encapsulado = encapsulado.get("name", "")

        nome_esperado = nome_adesivo.replace(
            "Sticker | ",
            "Sticker Slab | ",
            1,
        )

        if nome_esperado != nome_encapsulado:
            nomes_diferentes.append(
                (
                    chave,
                    nome_adesivo,
                    nome_encapsulado,
                )
            )

    print("\nSKINEXA - CORRESPONDENCIA DE ADESIVOS")
    print("=" * 50)

    print(f"Adesivos pendentes: {len(adesivos)}")
    print(f"Encapsulados pendentes: {len(encapsulados)}")
    print(f"Def_index correspondentes: {len(correspondentes)}")
    print(f"Somente adesivos: {len(somente_adesivos)}")
    print(f"Somente encapsulados: {len(somente_encapsulados)}")
    print(f"Tipos diferentes: {len(tipos_diferentes)}")
    print(f"Nomes diferentes: {len(nomes_diferentes)}")

    print("\nEXEMPLOS DE DIFERENCAS")
    print("-" * 50)

    for diferenca in nomes_diferentes[:10]:
        print(diferenca)

    print("\nDISTRIBUICAO DOS TIPOS CORRESPONDENTES")
    print("-" * 50)

    tipos = Counter(
        adesivos[chave].get("type")
        for chave in correspondentes
    )

    for tipo, quantidade in sorted(
        tipos.items(),
        key=lambda par: str(par[0]),
    ):
        print(f"{tipo}: {quantidade}")

    print("\nNenhum registro foi gravado no MySQL.")

    return 0

if __name__ == "__main__":
    raise SystemExit(auditar_correspondencia())