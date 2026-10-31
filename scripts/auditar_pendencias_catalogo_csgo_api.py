"""Audita registros da CSGO-API sem identidade comercial conhecida."""

from collections import Counter
from typing import Any

from skinexa.integrations.catalogo.csgo_api_client import (
    buscar_itens_csgo_api,
)

from skinexa.services.catalogo.normalizacao_itens_adicionais import (
    normalizar_lote_itens_adicionais_csgo_api,
)

CATEGORIAS_PENDENTES = (
    "adesivos",
    "caixas",
    "grafites",
    "musicas",
    "colecionaveis",
    "adesivos_encapsulados",
    "chaves",
)

CAMPOS_ANALISE = (
    "premier_season",
    "rarity",
    "marketable",
    "exclusive",
    "genuine",
    "type",
    "tint",
    "color_index",
)

LIMITE_EXEMPLOS = 5

def sem_identidade_comercial(registro: dict[str, Any]) -> bool:
    """Identifica registros sem market_hash_name válido."""

    nome_mercado = registro.get("market_hash_name")

    return not (
        isinstance(nome_mercado, str)
        and nome_mercado.strip()
    )

def resumir_valor(valor: Any) -> str:
    """Representa valores da origem sem perder o tipo básico."""

    if valor is None:
        return "None"

    if isinstance(valor, bool):
        return str(valor)

    if isinstance(valor, dict):
        return "dict"

    if isinstance(valor, list):
        return "list"

    return str(valor)[:100]

def auditar_pendencias_catalogo() -> int:
    """Analisa pendências por categoria sem persistir dados."""

    print("\nSKINEXA - AUDITORIA DE PENDENCIAS")
    print("=" * 50)

    total_pendentes = 0
    ids_pendentes = set()
    total_motivos = Counter()

    for categoria in CATEGORIAS_PENDENTES:
        registros = buscar_itens_csgo_api(
            categoria
        )

        relatorio = normalizar_lote_itens_adicionais_csgo_api(
            registros,
            categoria=categoria,
        )

        motivos_pendencias = Counter(
            pendente.motivo
            for pendente in relatorio.pendentes
        )
        
        total_motivos.update(
            motivos_pendencias
        )
        
        pendentes = [
            registro
            for registro in registros
            if sem_identidade_comercial(registro)
        ]

        if len(pendentes) != (
            relatorio.total_sem_identidade_comercial
        ):
            raise RuntimeError(
                f"Classificação divergente: {categoria}"
            )

        if relatorio.total_rejeitados:
            raise RuntimeError(
                f"Registros rejeitados: {categoria}"
            )

        total_pendentes += len(pendentes)

        print(f"\nCATEGORIA: {categoria.upper()}")
        print("-" * 50)
        print(f"Total pendente: {len(pendentes)}")

        print("\nCLASSIFICACAO DAS PENDENCIAS")
        print("-" * 50)

        for motivo, quantidade in sorted(
            motivos_pendencias.items()
        ):
            print(
                f"{motivo}: {quantidade}"
            )
        
        campos = Counter()

        for registro in pendentes:
            identificador = registro.get("id")

            chave = (categoria, identificador)

            if chave in ids_pendentes:
                raise RuntimeError(
                    f"ID repetido: {chave}"
                )

            ids_pendentes.add(chave)
            campos.update(registro.keys())

        print("\nCAMPOS DISPONIVEIS")

        for campo, quantidade in sorted(campos.items()):
            print(f"{campo}: {quantidade}")

        print("\nATRIBUTOS RELEVANTES")

        for campo in CAMPOS_ANALISE:
            valores = Counter(
                resumir_valor(registro.get(campo))
                for registro in pendentes
            )

            if campo not in campos:
                continue

            print(f"\n{campo}:")

            for valor, quantidade in valores.most_common(10):
                print(
                    f"  {valor}: {quantidade}"
                )

        print("\nEXEMPLOS DE PENDENCIAS")

        for registro in pendentes[:LIMITE_EXEMPLOS]:
            exemplo = {
                "id": registro.get("id"),
                "name": registro.get("name"),
                "market_hash_name": registro.get(
                    "market_hash_name"
                ),
                "def_index": registro.get("def_index"),
                "type": registro.get("type"),
                "marketable": registro.get("marketable"),
                "exclusive": registro.get("exclusive"),
                "genuine": registro.get("genuine"),
            }

            print(exemplo)
        
        if categoria in ("caixas", "musicas", "chaves"):
            print("\nTODOS OS REGISTROS PENDENTES")
            print("-" * 50)

            for registro in pendentes:
                print(
                    {
                        "id": registro.get("id"),
                        "name": registro.get("name"),
                        "type": registro.get("type"),
                        "marketable": registro.get("marketable"),
                        "exclusive": registro.get("exclusive"),
                    }
                )
        
        if categoria == "colecionaveis":
            print("\nCOLECIONAVEIS POR TIPO")
            print("-" * 50)

            distribuicao = Counter(
                str(registro.get("type") or "Sem tipo")
                for registro in pendentes
            )

            for tipo, quantidade in sorted(
                distribuicao.items()
            ):
                print(
                    f"{tipo}: {quantidade}"
                )

    print("\nRESULTADO CONSOLIDADO")
    print("-" * 50)
    print(f"Categorias analisadas: {len(CATEGORIAS_PENDENTES)}")
    print(f"Registros pendentes: {total_pendentes}")
    
    print("\nDISTRIBUICAO GLOBAL DOS MOTIVOS")
    print("-" * 50)

    for motivo, quantidade in sorted(
        total_motivos.items()
    ):
        print(
            f"{motivo}: {quantidade}"
        )

    if sum(total_motivos.values()) != total_pendentes:
        raise RuntimeError(
            "A classificação das pendências "
            "não corresponde ao total auditado."
        )

    if total_pendentes != len(ids_pendentes):
        raise RuntimeError(
            "Existem identificadores duplicados."
        )

    print("\nAuditoria concluida com sucesso.")
    print("Nenhum registro foi gravado no MySQL.")

    return 0

if __name__ == "__main__":
    raise SystemExit(
        auditar_pendencias_catalogo()
    )