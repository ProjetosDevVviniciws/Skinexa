"""Normalização dos itens fornecidos pela CSGO-API."""

from decimal import Decimal, InvalidOperation

from typing import Any

from skinexa.dto.catalogo.importacao import (
    ItemImportacaoCatalogoDTO,
)

APP_ID_CS2 = 730

TIPOS_ITENS_CSGO_API = {
    # Categorias presentes na resposta real da CSGO-API.
    "csgo_inventory_weapon_category_pistols": "pistola",
    "csgo_inventory_weapon_category_rifles": "rifle",
    "csgo_inventory_weapon_category_smgs": "submetralhadora",
    "csgo_inventory_weapon_category_heavy": "pesada",
    "loadoutslot_equipment": "equipamento",
    "sfui_invpanel_filter_gloves": "luva",
    "sfui_invpanel_filter_melee": "faca",

    # Identificadores alternativos já previstos.
    "sfui_invpanel_filter_knife": "faca",
    "sfui_invpanel_filter_pistol": "pistola",
    "sfui_invpanel_filter_rifle": "rifle",
    "sfui_invpanel_filter_smg": "submetralhadora",
    "sfui_invpanel_filter_shotgun": "escopeta",
    "sfui_invpanel_filter_machinegun": "metralhadora",
}

class ErroNormalizacaoCSGOAPI(ValueError):
    """Representa dados inválidos durante a normalização."""

def _obter_texto(
    valor: Any,
) -> str | None:
    """Normaliza um valor textual opcional."""

    if not isinstance(valor, str):
        return None

    texto = valor.strip()

    return texto or None

def _obter_nome_objeto(
    valor: Any,
) -> str | None:
    """Extrai o campo name de um objeto externo."""

    if not isinstance(valor, dict):
        return None

    return _obter_texto(valor.get("name"))

def _obter_decimal(
    valor: Any,
) -> Decimal | None:
    """Converte valores numéricos externos para Decimal."""

    if valor is None:
        return None

    if isinstance(valor, bool):
        raise ErroNormalizacaoCSGOAPI(
            "Valor decimal inválido."
        )

    try:
        resultado = Decimal(str(valor))
    except (InvalidOperation, ValueError, TypeError) as erro:
        raise ErroNormalizacaoCSGOAPI(
            "Valor decimal inválido."
        ) from erro

    if not resultado.is_finite():
        raise ErroNormalizacaoCSGOAPI(
            "Valor decimal inválido."
        )

    if not Decimal("0") <= resultado <= Decimal("1"):
        raise ErroNormalizacaoCSGOAPI(
            "O float deve estar entre 0 e 1."
        )

    return resultado

def _obter_indice_pintura(
    valor: Any,
) -> int | None:
    """Converte o paint index para inteiro."""

    if valor is None:
        return None

    if isinstance(valor, bool):
        raise ErroNormalizacaoCSGOAPI(
            "Índice de pintura inválido."
        )

    if not isinstance(valor, (str, int)):
        raise ErroNormalizacaoCSGOAPI(
            "Índice de pintura inválido."
        )

    try:
        indice = int(valor)
    except ValueError as erro:
        raise ErroNormalizacaoCSGOAPI(
            "Índice de pintura inválido."
        ) from erro

    if not 0 <= indice <= 4294967295:
        raise ErroNormalizacaoCSGOAPI(
            "Índice de pintura fora do intervalo permitido."
        )

    return indice

def _obter_booleano(
    valor: Any,
    *,
    campo: str,
) -> bool:
    """Valida um booleano recebido da fonte externa."""

    if not isinstance(valor, bool):
        raise ErroNormalizacaoCSGOAPI(
            f"O campo {campo} deve ser booleano."
        )

    return valor

def _obter_tipo_item(
    categoria: Any,
) -> str:
    """Converte a categoria externa para o domínio Skinexa."""

    if not isinstance(categoria, dict):
        raise ErroNormalizacaoCSGOAPI(
            "Categoria do item inválida."
        )

    identificador = _obter_texto(
        categoria.get("id")
    )

    if identificador is None:
        raise ErroNormalizacaoCSGOAPI(
            "Categoria do item não identificada."
        )

    tipo_item = TIPOS_ITENS_CSGO_API.get(
        identificador
    )

    if tipo_item is None:
        raise ErroNormalizacaoCSGOAPI(
            f"Categoria ainda não mapeada: {identificador}"
        )

    return tipo_item

def normalizar_item_skin_csgo_api(
    registro: dict[str, Any],
) -> ItemImportacaoCatalogoDTO:
    """Normaliza um item do conjunto de skins da CSGO-API."""

    if not isinstance(registro, dict):
        raise ErroNormalizacaoCSGOAPI(
            "Registro de item inválido."
        )

    nome_mercado = _obter_texto(
        registro.get("market_hash_name")
    )

    if nome_mercado is None:
        raise ErroNormalizacaoCSGOAPI(
            "Item sem market_hash_name válido."
        )

    if len(nome_mercado) > 255:
        raise ErroNormalizacaoCSGOAPI(
            "Nome de mercado excede 255 caracteres."
        )

    nome_exibicao = (
        _obter_texto(registro.get("name"))
        or nome_mercado
    )

    if len(nome_exibicao) > 255:
        raise ErroNormalizacaoCSGOAPI(
            "Nome de exibição excede 255 caracteres."
        )

    tipo_item = _obter_tipo_item(
        registro.get("category")
    )

    nome_arma = _obter_nome_objeto(
        registro.get("weapon")
    )

    nome_acabamento = _obter_nome_objeto(
        registro.get("pattern")
    )

    estado_exterior = _obter_nome_objeto(
        registro.get("wear")
    )

    raridade = _obter_nome_objeto(
        registro.get("rarity")
    )

    float_minimo = _obter_decimal(
        registro.get("min_float")
    )

    float_maximo = _obter_decimal(
        registro.get("max_float")
    )

    if (
        float_minimo is not None
        and float_maximo is not None
        and float_minimo > float_maximo
    ):
        raise ErroNormalizacaoCSGOAPI(
            "Intervalo de float inválido."
        )

    variante_stattrak = _obter_booleano(
        registro.get("stattrak", False),
        campo="stattrak",
    )

    variante_souvenir = _obter_booleano(
        registro.get("souvenir", False),
        campo="souvenir",
    )

    indice_pintura = _obter_indice_pintura(
        registro.get("paint_index")
    )

    url_imagem = _obter_texto(
        registro.get("image")
    )

    identificador_externo = _obter_texto(
        registro.get("id")
    )

    identificador_skin = _obter_texto(
        registro.get("skin_id")
    )

    metadados_origem = {
        "fonte": "csgo_api",
        "id_externo": identificador_externo,
        "skin_id": identificador_skin,
    }

    return ItemImportacaoCatalogoDTO(
        app_id=APP_ID_CS2,
        nome_mercado=nome_mercado,
        nome_exibicao=nome_exibicao,
        tipo_item=tipo_item,
        nome_arma=nome_arma,
        nome_acabamento=nome_acabamento,
        estado_exterior=estado_exterior,
        raridade=raridade,
        descricao=_obter_texto(
            registro.get("description")
        ),
        indice_pintura=indice_pintura,
        float_minimo=float_minimo,
        float_maximo=float_maximo,
        variante_stattrak=variante_stattrak,
        variante_souvenir=variante_souvenir,
        url_icone_grande=url_imagem,
        metadados_origem=metadados_origem,
    )