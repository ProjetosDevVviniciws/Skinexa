from typing import Any, Iterable

from skinexa.dto.steam.inventario import (
    InstanciaItemSteamDTO,
    ItemCatalogoSteamDTO,
    ItemInventarioSteamDTO,
)

from skinexa.integrations.steam.inventario import (
    InventarioSteamBruto,
)

URL_IMAGEM_STEAM = "https://community.cloudflare.steamstatic.com/economy/image"

class ErroNormalizacaoInventarioSteam(RuntimeError):
    """Erro ao transformar o inventário bruto em DTOs internos."""

def normalizar_inventario_steam(
    inventario: InventarioSteamBruto,
) -> tuple[ItemInventarioSteamDTO, ...]:
    """
    Combina assets e descriptions retornados pela Steam.

    A ligação é feita pelo par:
    classid + instanceid.
    """

    descricoes_indexadas = _indexar_descricoes(
        inventario.descricoes
    )

    itens_normalizados: list[ItemInventarioSteamDTO] = []

    for ativo in inventario.ativos:
        chave = _criar_chave_item(
            class_id=ativo.get("classid"),
            instance_id=ativo.get("instanceid"),
        )

        descricao = descricoes_indexadas.get(chave)

        if descricao is None:
            raise ErroNormalizacaoInventarioSteam(
                "Não foi encontrada uma descrição para o item "
                f"asset_id={ativo.get('assetid')}."
            )

        catalogo = _normalizar_item_catalogo(
            descricao=descricao,
            app_id=inventario.app_id,
        )

        instancia = _normalizar_instancia(
            ativo=ativo,
            descricao=descricao,
            steam_id=inventario.steam_id,
            app_id=inventario.app_id,
            contexto_id=str(inventario.contexto_id),
        )

        itens_normalizados.append(
            ItemInventarioSteamDTO(
                catalogo=catalogo,
                instancia=instancia,
            )
        )

    return tuple(itens_normalizados)

def _indexar_descricoes(
    descricoes: Iterable[dict[str, Any]],
) -> dict[tuple[str, str], dict[str, Any]]:
    """Cria um índice por classid e instanceid."""

    indice: dict[
        tuple[str, str],
        dict[str, Any],
    ] = {}

    for descricao in descricoes:
        chave = _criar_chave_item(
            class_id=descricao.get("classid"),
            instance_id=descricao.get("instanceid"),
        )

        indice[chave] = descricao

    return indice

def _criar_chave_item(
    *,
    class_id: Any,
    instance_id: Any,
) -> tuple[str, str]:
    """Normaliza a chave utilizada para relacionar os dados."""

    class_id_normalizado = str(class_id or "").strip()
    instance_id_normalizado = str(
        instance_id or "0"
    ).strip()

    if not class_id_normalizado:
        raise ErroNormalizacaoInventarioSteam(
            "Um item do inventário não possui classid."
        )

    return (
        class_id_normalizado,
        instance_id_normalizado,
    )

def _normalizar_item_catalogo(
    *,
    descricao: dict[str, Any],
    app_id: int,
) -> ItemCatalogoSteamDTO:
    """Transforma uma descrição da Steam em item de catálogo."""

    nome_mercado = _obter_texto(
        descricao.get("market_hash_name")
    )

    nome_exibicao = (
        _obter_texto(descricao.get("name"))
        or nome_mercado
    )

    if not nome_mercado:
        raise ErroNormalizacaoInventarioSteam(
            "A descrição do item não possui market_hash_name."
        )

    tags = _normalizar_tags(descricao.get("tags"))

    tipo_item = (
        _buscar_tag(
            tags,
            "type",
            "tipo",
        )
        or _obter_texto(descricao.get("type"))
        or "outro"
    )

    nome_arma = _buscar_tag(
        tags,
        "weapon",
        "arma",
    )

    estado_exterior = _buscar_tag(
        tags,
        "exterior",
        "estado",
    )

    raridade = _buscar_tag(
        tags,
        "rarity",
        "raridade",
    )

    qualidade = _buscar_tag(
        tags,
        "quality",
        "qualidade",
    )

    colecao = _buscar_tag(
        tags,
        "itemset",
        "collection",
        "colecao",
    )

    descricao_texto = _extrair_descricao(
        descricao.get("descriptions")
    )

    variante_stattrak = _detectar_stattrak(
        nome_mercado=nome_mercado,
        qualidade=qualidade,
    )

    variante_souvenir = _detectar_souvenir(
        nome_mercado=nome_mercado,
        qualidade=qualidade,
    )

    return ItemCatalogoSteamDTO(
        app_id=app_id,
        nome_mercado=nome_mercado,
        nome_exibicao=nome_exibicao,
        tipo_item=tipo_item,
        nome_arma=nome_arma,
        nome_acabamento=_extrair_nome_acabamento(
            nome_mercado
        ),
        estado_exterior=estado_exterior,
        raridade=raridade,
        qualidade=qualidade,
        colecao=colecao,
        descricao=descricao_texto,
        indice_pintura=None,
        float_minimo=None,
        float_maximo=None,
        variante_stattrak=variante_stattrak,
        variante_souvenir=variante_souvenir,
        comercializavel=_converter_booleano(
            descricao.get("marketable")
        ),
        trocavel=_converter_booleano(
            descricao.get("tradable")
        ),
        mercadoria_generica=_converter_booleano(
            descricao.get("commodity")
        ),
        steam_class_id=str(descricao["classid"]),
        steam_instance_id=str(
            descricao.get("instanceid") or "0"
        ),
        url_icone=_montar_url_imagem(
            descricao.get("icon_url")
        ),
        url_icone_grande=_montar_url_imagem(
            descricao.get("icon_url_large")
        ),
        tags=tags,
        metadados_origem=dict(descricao),
    )

def _normalizar_instancia(
    *,
    ativo: dict[str, Any],
    descricao: dict[str, Any],
    steam_id: str,
    app_id: int,
    contexto_id: str,
) -> InstanciaItemSteamDTO:
    """Transforma um asset da Steam em instância individual."""

    asset_id = _obter_texto(ativo.get("assetid"))

    if not asset_id:
        raise ErroNormalizacaoInventarioSteam(
            "Um item do inventário não possui assetid."
        )

    quantidade = _converter_inteiro(
        ativo.get("amount"),
        padrao=1,
    )

    if quantidade < 1:
        raise ErroNormalizacaoInventarioSteam(
            f"O item asset_id={asset_id} possui quantidade inválida."
        )

    nome_mercado = _obter_texto(
        descricao.get("market_hash_name")
    )

    qualidade = _buscar_tag(
        _normalizar_tags(descricao.get("tags")),
        "quality",
        "qualidade",
    )

    return InstanciaItemSteamDTO(
        steam_id_usuario=steam_id,
        app_id=app_id,
        contexto_id=str(
            ativo.get("contextid") or contexto_id
        ),
        asset_id=asset_id,
        class_id=str(ativo.get("classid") or ""),
        instance_id=str(
            ativo.get("instanceid") or "0"
        ),
        quantidade=quantidade,
        indice_definicao=None,
        indice_pintura=None,
        semente_pintura=None,
        valor_float=None,
        nome_personalizado=_extrair_nome_personalizado(
            descricao
        ),
        link_inspecao=_extrair_link_inspecao(
            descricao=descricao,
            asset_id=asset_id,
            steam_id=steam_id,
        ),
        stattrak=_detectar_stattrak(
            nome_mercado=nome_mercado,
            qualidade=qualidade,
        ),
        contador_stattrak=None,
        souvenir=_detectar_souvenir(
            nome_mercado=nome_mercado,
            qualidade=qualidade,
        ),
        trocavel=_converter_booleano(
            descricao.get("tradable")
        ),
        comercializavel=_converter_booleano(
            descricao.get("marketable")
        ),
        bloqueado_ate=None,
        fonte_dados="steam",
        metadados_origem={
            "asset": dict(ativo),
            "description": dict(descricao),
        },
    )

def _normalizar_tags(
    valor: Any,
) -> tuple[dict[str, Any], ...]:
    """Mantém apenas tags representadas por objetos válidos."""

    if not isinstance(valor, list):
        return ()

    return tuple(
        dict(tag)
        for tag in valor
        if isinstance(tag, dict)
    )

def _buscar_tag(
    tags: tuple[dict[str, Any], ...],
    *categorias: str,
) -> str | None:
    """Busca o valor localizado de uma categoria de tag."""

    categorias_normalizadas = {
        categoria.casefold()
        for categoria in categorias
    }

    for tag in tags:
        categoria = _obter_texto(
            tag.get("category")
        )

        categoria_localizada = _obter_texto(
            tag.get("localized_category_name")
        )

        categorias_encontradas = {
            valor.casefold()
            for valor in (
                categoria,
                categoria_localizada,
            )
            if valor
        }

        if not (
            categorias_encontradas
            & categorias_normalizadas
        ):
            continue

        return (
            _obter_texto(
                tag.get("localized_tag_name")
            )
            or _obter_texto(tag.get("name"))
            or _obter_texto(
                tag.get("internal_name")
            )
        )

    return None

def _extrair_nome_acabamento(
    nome_mercado: str,
) -> str | None:
    """
    Extrai o acabamento de nomes como:

    AK-47 | Redline (Field-Tested)
    """

    if "|" not in nome_mercado:
        return None

    acabamento = nome_mercado.split("|", 1)[1].strip()

    if acabamento.endswith(")") and "(" in acabamento:
        acabamento = acabamento.rsplit("(", 1)[0].strip()

    return acabamento or None

def _extrair_descricao(
    descricoes: Any,
) -> str | None:
    """Combina textos públicos relevantes da descrição."""

    if not isinstance(descricoes, list):
        return None

    valores: list[str] = []

    for descricao in descricoes:
        if not isinstance(descricao, dict):
            continue

        valor = _obter_texto(descricao.get("value"))

        if not valor:
            continue

        if valor not in valores:
            valores.append(valor)

    if not valores:
        return None

    return "\n".join(valores)

def _extrair_nome_personalizado(
    descricao: dict[str, Any],
) -> str | None:
    """Obtém o nome personalizado quando fornecido pela Steam."""

    return _obter_texto(
        descricao.get("name_color")
    ) if descricao.get("custom_name") else None

def _extrair_link_inspecao(
    *,
    descricao: dict[str, Any],
    asset_id: str,
    steam_id: str,
) -> str | None:
    """Localiza e preenche o link de inspeção do item."""

    acoes = descricao.get("actions")

    if not isinstance(acoes, list):
        return None

    for acao in acoes:
        if not isinstance(acao, dict):
            continue

        link = _obter_texto(acao.get("link"))

        if not link:
            continue

        link_normalizado = link.casefold()

        if (
            "csgo_econ_action_preview" not in link_normalizado
            and "%assetid%" not in link_normalizado
        ):
            continue

        return (
            link.replace(
                "%owner_steamid%",
                steam_id,
            )
            .replace(
                "%assetid%",
                asset_id,
            )
        )

    return None

def _detectar_stattrak(
    *,
    nome_mercado: str | None,
    qualidade: str | None,
) -> bool:
    texto = " ".join(
        valor
        for valor in (
            nome_mercado,
            qualidade,
        )
        if valor
    ).casefold()

    return "stattrak" in texto

def _detectar_souvenir(
    *,
    nome_mercado: str | None,
    qualidade: str | None,
) -> bool:
    texto = " ".join(
        valor
        for valor in (
            nome_mercado,
            qualidade,
        )
        if valor
    ).casefold()

    return "souvenir" in texto

def _montar_url_imagem(
    caminho: Any,
) -> str | None:
    caminho_normalizado = _obter_texto(caminho)

    if not caminho_normalizado:
        return None

    if caminho_normalizado.startswith(
        ("http://", "https://")
    ):
        return caminho_normalizado

    return f"{URL_IMAGEM_STEAM}/{caminho_normalizado}"


def _converter_booleano(valor: Any) -> bool:
    return valor in {
        1,
        "1",
        True,
        "true",
        "True",
    }

def _converter_inteiro(
    valor: Any,
    *,
    padrao: int,
) -> int:
    try:
        return int(valor)
    except (TypeError, ValueError):
        return padrao

def _obter_texto(valor: Any) -> str | None:
    if valor is None:
        return None

    texto = str(valor).strip()

    return texto or None