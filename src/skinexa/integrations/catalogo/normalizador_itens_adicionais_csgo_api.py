"""Normaliza categorias adicionais do catálogo da CSGO-API."""

from typing import Any

from skinexa.dto.catalogo.importacao import (
    ItemImportacaoCatalogoDTO,
)

TIPOS_ITENS_ADICIONAIS = {
    "adesivos": "adesivo",
    "caixas": "caixa",
    "agentes": "agente",
    "patches": "patch",
    "chaveiros": "chaveiro",
    "grafites": "grafite",
    "musicas": "musica",
    "colecionaveis": "colecionavel",
    "adesivos_encapsulados": "adesivo_encapsulado",
    "chaves": "chave",
    "destaques": "destaque",
}

class ErroNormalizacaoItemAdicionalCSGOAPI(ValueError):
    """Representa uma falha na normalização de um item adicional."""

def normalizar_item_adicional_csgo_api(
    registro: dict[str, Any],
    *,
    categoria: str,
) -> ItemImportacaoCatalogoDTO:
    """Normaliza um item adicional com identidade comercial conhecida."""

    if categoria not in TIPOS_ITENS_ADICIONAIS:
        raise ErroNormalizacaoItemAdicionalCSGOAPI(
            f"Categoria não suportada: {categoria}"
        )

    if not isinstance(registro, dict):
        raise ErroNormalizacaoItemAdicionalCSGOAPI(
            "O registro deve ser um dicionário."
        )

    identificador = registro.get("id")
    nome = registro.get("name")
    nome_mercado = registro.get("market_hash_name")
    imagem = registro.get("image")

    if not isinstance(identificador, str) or not identificador.strip():
        raise ErroNormalizacaoItemAdicionalCSGOAPI(
            "Registro sem ID externo válido."
        )

    if not isinstance(nome, str) or not nome.strip():
        raise ErroNormalizacaoItemAdicionalCSGOAPI(
            "Registro sem nome válido."
        )

    if not isinstance(nome_mercado, str) or not nome_mercado.strip():
        raise ErroNormalizacaoItemAdicionalCSGOAPI(
            "Registro sem identidade comercial conhecida."
        )

    if not isinstance(imagem, str) or not imagem.strip():
        raise ErroNormalizacaoItemAdicionalCSGOAPI(
            "Registro sem imagem válida."
        )

    raridade_origem = registro.get("rarity")

    raridade = None

    if isinstance(raridade_origem, dict):
        nome_raridade = raridade_origem.get("name")

        if isinstance(nome_raridade, str):
            raridade = nome_raridade

    descricao = registro.get("description")

    if not isinstance(descricao, str):
        descricao = None

    campos_metadados = {
        "def_index",
        "type",
        "effect",
        "player",
        "team",
        "tournament",
        "collections",
        "first_sale_date",
        "model_player",
        "rental",
        "special_notes",
        "original",
        "icon_base",
        "color_index",
        "tint",
        "exclusive",
        "genuine",
        "premier_season",
        "marketable",
        "map",
        "stage",
        "team0",
        "team1",
        "thumbnail",
        "tournament_event",
        "tournament_player",
        "video",
    }

    metadados_origem = {
        "fonte": "csgo_api",
        "categoria_origem": categoria,
        "id_externo": identificador,
        "nome_origem": nome,
        "raridade_origem": raridade_origem,
    }

    for campo in campos_metadados:
        if campo in registro:
            metadados_origem[campo] = registro[campo]

    return ItemImportacaoCatalogoDTO(
        app_id=730,
        nome_mercado=nome_mercado,
        nome_exibicao=nome,
        tipo_item=TIPOS_ITENS_ADICIONAIS[categoria],
        raridade=raridade,
        descricao=descricao,
        comercializavel=False,
        url_icone_grande=imagem,
        metadados_origem=metadados_origem,
    )