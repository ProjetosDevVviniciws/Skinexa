"""Audita as estruturas das novas categorias do catálogo CS2."""

from collections import Counter

from typing import Any

from skinexa.integrations.catalogo.csgo_api_client import (
    ARQUIVOS_CATALOGO,
    buscar_itens_csgo_api,
)

from skinexa.services.catalogo.normalizacao_itens_adicionais import (
    normalizar_lote_itens_adicionais_csgo_api,
)

from skinexa.integrations.catalogo.normalizador_itens_adicionais_csgo_api import (
    TIPOS_ITENS_ADICIONAIS,
)

CATEGORIAS_AUDITORIA = (
    "patches",
    "chaveiros",
    "grafites",
    "musicas",
    "colecionaveis",
    "adesivos_encapsulados",
    "chaves",
    "destaques",
    "armas_base",
    "pets",
)

def auditar_categoria(
    categoria: str,
    registros: list[dict[str, Any]],
) -> None:
    """Analisa os campos e identificadores de uma categoria."""

    print(f"\nCATEGORIA: {categoria.upper()}")
    print("-" * 50)

    campos = Counter()
    tipos = Counter()

    total_com_id = 0
    total_com_nome = 0
    total_com_nome_mercado = 0
    total_com_imagem = 0

    nomes_comerciais = Counter()
    ids_externos = Counter()

    for registro in registros:
        campos.update(
            registro.keys()
        )

        identificador = registro.get("id")
        nome = registro.get("name")
        nome_mercado = registro.get(
            "market_hash_name"
        )
        imagem = registro.get("image")
        tipo = registro.get("type")

        if identificador:
            total_com_id += 1

            ids_externos[
                str(identificador)
            ] += 1

        if nome:
            total_com_nome += 1

        if nome_mercado:
            total_com_nome_mercado += 1

            nomes_comerciais[
                str(nome_mercado)
            ] += 1

        if imagem:
            total_com_imagem += 1

        if tipo is not None:
            tipos[str(tipo)] += 1

    print(
        f"Total de registros: {len(registros)}"
    )

    print(
        f"Registros com ID externo: {total_com_id}"
    )

    print(
        f"Registros com nome: {total_com_nome}"
    )

    print(
        "Registros com market_hash_name: "
        f"{total_com_nome_mercado}"
    )

    print(
        f"Registros com imagem: {total_com_imagem}"
    )

    ids_duplicados = {
        identificador: quantidade
        for identificador, quantidade
        in ids_externos.items()
        if quantidade > 1
    }

    nomes_duplicados = {
        nome: quantidade
        for nome, quantidade
        in nomes_comerciais.items()
        if quantidade > 1
    }

    print(
        f"IDs externos duplicados: "
        f"{len(ids_duplicados)}"
    )

    print(
        f"Nomes comerciais duplicados: "
        f"{len(nomes_duplicados)}"
    )

    print("\nCAMPOS DISPONIVEIS")
    print("-" * 50)

    for campo, quantidade in sorted(
        campos.items()
    ):
        print(
            f"{campo}: {quantidade}"
        )

    print("\nTIPOS ENCONTRADOS")
    print("-" * 50)

    if tipos:
        for tipo, quantidade in sorted(
            tipos.items()
        ):
            print(
                f"{tipo}: {quantidade}"
            )
    else:
        print(
            "Nenhum tipo informado."
        )

    print("\nEXEMPLOS DE REGISTROS")
    print("-" * 50)

    for registro in registros[:3]:
        print(
            {
                "id": registro.get("id"),
                "name": registro.get("name"),
                "market_hash_name": registro.get(
                    "market_hash_name"
                ),
                "def_index": registro.get(
                    "def_index"
                ),
                "type": registro.get("type"),
                "rarity": registro.get("rarity"),
                "image": registro.get("image"),
            }
        )

    if nomes_duplicados:
        print("\nEXEMPLOS DE NOMES DUPLICADOS")
        print("-" * 50)

        for nome, quantidade in list(
            nomes_duplicados.items()
        )[:10]:
            print(
                f"{quantidade} | {nome}"
            )

def auditar_normalizacao_categoria(
    categoria: str,
    registros: list[dict[str, Any]],
) -> None:
    """Valida a normalização de uma categoria com dados reais."""

    print(
        f"\nNORMALIZACAO EM LOTE: {categoria.upper()}"
    )
    print("-" * 50)

    relatorio = normalizar_lote_itens_adicionais_csgo_api(
        registros,
        categoria=categoria,
    )

    print(
        f"Registros recebidos: {relatorio.total_recebidos}"
    )

    print(
        f"Itens normalizados: {relatorio.total_normalizados}"
    )

    print(
        "Sem identidade comercial: "
        f"{relatorio.total_sem_identidade_comercial}"
    )

    print(
        f"Registros rejeitados: {relatorio.total_rejeitados}"
    )

    print(
        f"Duplicacoes comerciais: {relatorio.total_duplicados}"
    )

    print(
        "Variantes normalizadas: "
        f"{relatorio.total_variantes_normalizadas}"
    )

    print(
        "Variantes duplicadas: "
        f"{relatorio.total_variantes_duplicadas}"
    )

    chaves_comerciais = {
        (
            item.app_id,
            item.nome_mercado,
        )
        for item in relatorio.itens
    }

    variantes_sem_item = [
        variante
        for variante in relatorio.variantes
        if (
            variante.app_id,
            variante.nome_mercado,
        ) not in chaves_comerciais
    ]

    print(
        f"Variantes sem item comercial: "
        f"{len(variantes_sem_item)}"
    )

    if variantes_sem_item:
        raise RuntimeError(
            "Foram encontradas variantes sem item comercial."
        )
    
    chaves_variantes = {
        (
            variante.fonte,
            variante.id_externo,
        )
        for variante in relatorio.variantes
    }

    if len(chaves_variantes) != len(relatorio.variantes):
        raise RuntimeError(
            "Foram encontradas variantes externas duplicadas."
        )

    for variante in relatorio.variantes:
        if variante.fonte != "csgo_api":
            raise RuntimeError(
                "Foi encontrada uma variante com fonte inesperada."
            )

        if variante.skin_id_externo is not None:
            raise RuntimeError(
                "Uma variante adicional recebeu um ID de skin."
            )

        if variante.indice_pintura is not None:
            raise RuntimeError(
                "Uma variante adicional recebeu um índice de pintura."
            )

        if variante.identificador_acabamento is not None:
            raise RuntimeError(
                "Uma variante adicional recebeu um identificador de acabamento."
            )
        
    print(
        "Identificadores externos validados com sucesso."
    )
    
    total_classificados = (
        relatorio.total_normalizados
        + relatorio.total_sem_identidade_comercial
        + relatorio.total_rejeitados
        + relatorio.total_duplicados
    )

    print(
        f"Total classificado: {total_classificados}"
    )

    if total_classificados != relatorio.total_recebidos:
        raise RuntimeError(
            "A normalização não classificou "
            "todos os registros recebidos."
        )

    total_variantes_classificadas = (
        relatorio.total_variantes_normalizadas
        + relatorio.total_variantes_duplicadas
    )

    total_registros_elegiveis = (
        relatorio.total_recebidos
        - relatorio.total_sem_identidade_comercial
        - relatorio.total_rejeitados
    )

    print(
        "Registros elegíveis para variantes: "
        f"{total_registros_elegiveis}"
    )

    print(
        "Variantes classificadas: "
        f"{total_variantes_classificadas}"
    )

    if total_variantes_classificadas != total_registros_elegiveis:
        raise RuntimeError(
            "A classificação das variantes apresentou inconsistências."
        )
    
    print("\nMOTIVOS DE REJEICAO")
    print("-" * 50)

    if relatorio.motivos_rejeicao:
        for motivo, quantidade in sorted(
            relatorio.motivos_rejeicao.items()
        ):
            print(
                f"{quantidade} | {motivo}"
            )
    else:
        print("Nenhuma rejeicao encontrada.")

    print("\nEXEMPLOS DE ITENS NORMALIZADOS")
    print("-" * 50)

    for item in relatorio.itens[:3]:
        print(
            {
                "nome_mercado": item.nome_mercado,
                "nome_exibicao": item.nome_exibicao,
                "tipo_item": item.tipo_item,
                "raridade": item.raridade,
                "url_icone_grande": item.url_icone_grande,
                "id_externo": item.metadados_origem.get(
                    "id_externo"
                ) if item.metadados_origem else None,
            }
        )

    print("\nEXEMPLOS DE VARIANTES NORMALIZADAS")
    print("-" * 50)

    for variante in relatorio.variantes[:3]:
        print(
            {
                "app_id": variante.app_id,
                "nome_mercado": variante.nome_mercado,
                "fonte": variante.fonte,
                "id_externo": variante.id_externo,
                "url_imagem": variante.url_imagem,
            }
        )
    
    print("\nEXEMPLOS SEM IDENTIDADE COMERCIAL")
    print("-" * 50)

    for pendente in relatorio.pendentes[:5]:
        print(
            {
                "indice": pendente.indice,
                "id_externo": pendente.id_externo,
                "nome_exibicao": pendente.nome_exibicao,
            }
        )

    if relatorio.total_rejeitados > 0:
        raise RuntimeError(
            f"A categoria {categoria} apresentou "
            "registros rejeitados."
        )

    print(
        f"\nNormalizacao de {categoria} "
        "concluida com sucesso."
    )

def main() -> int:
    """Audita as categorias restantes da CSGO-API."""

    print("\nSKINEXA - AUDITORIA DE CATEGORIAS")
    print("=" * 50)

    print(
        f"Categorias selecionadas: "
        f"{len(CATEGORIAS_AUDITORIA)}"
    )

    total_registros = 0
    total_com_nome_mercado = 0
    total_sem_nome_mercado = 0

    for categoria in CATEGORIAS_AUDITORIA:
        registros = buscar_itens_csgo_api(
            categoria
        )

        auditar_categoria(
            categoria,
            registros,
        )

        total_registros += len(registros)

        for registro in registros:
            nome_mercado = registro.get(
                "market_hash_name"
            )

            if (
                isinstance(nome_mercado, str)
                and nome_mercado.strip()
            ):
                total_com_nome_mercado += 1
            else:
                total_sem_nome_mercado += 1

        if categoria in TIPOS_ITENS_ADICIONAIS:
            auditar_normalizacao_categoria(
                categoria,
                registros,
            )
        else:
            print("\nNORMALIZACAO")
            print("-" * 50)
            print(
                "Categoria aguardando implementação "
                "do normalizador."
            )

    print("\nRESUMO DA AUDITORIA")
    print("-" * 50)

    print(
        f"Categorias analisadas: "
        f"{len(CATEGORIAS_AUDITORIA)}"
    )

    print(
        f"Registros recebidos: "
        f"{total_registros}"
    )

    print(
        "Registros com identidade comercial: "
        f"{total_com_nome_mercado}"
    )

    print(
        "Registros sem identidade comercial: "
        f"{total_sem_nome_mercado}"
    )

    print("\nAUDITORIA CONCLUIDA")
    print("-" * 50)

    print(
        "Nenhum registro foi gravado no MySQL."
    )

    return 0

if __name__ == "__main__":
    raise SystemExit(
        main()
    )