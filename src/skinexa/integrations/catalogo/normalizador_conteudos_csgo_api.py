"""Normalização dos conteúdos dos contêineres da CSGO-API."""

from typing import Any

from skinexa.dto.catalogo.conteineres import (
    ConteudoConteinerCatalogoDTO,
)

FONTE_CSGO_API = "csgo_api"

TIPOS_CONTEUDOS_CSGO_API = {
    "contains",
    "contains_rare",
}

INDICE_PINTURA_MAXIMO = 4294967295

class ErroNormalizacaoConteudoCSGOAPI(ValueError):
    """Representa dados inválidos na normalização de conteúdos."""

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
    """Extrai o nome de um objeto fornecido pela origem."""

    if not isinstance(valor, dict):
        return None

    return _obter_texto(
        valor.get("name")
    )

def _obter_indice_pintura(
    valor: Any,
) -> int | None:
    """Converte o paint index externo para inteiro."""

    if valor is None:
        return None

    if isinstance(valor, bool):
        raise ErroNormalizacaoConteudoCSGOAPI(
            "Índice de pintura inválido."
        )

    if not isinstance(valor, (str, int)):
        raise ErroNormalizacaoConteudoCSGOAPI(
            "Índice de pintura inválido."
        )

    try:
        indice = int(valor)
    except ValueError as erro:
        raise ErroNormalizacaoConteudoCSGOAPI(
            "Índice de pintura inválido."
        ) from erro

    if not 0 <= indice <= INDICE_PINTURA_MAXIMO:
        raise ErroNormalizacaoConteudoCSGOAPI(
            "Índice de pintura fora do intervalo permitido."
        )

    return indice

def normalizar_conteudo_csgo_api(
    registro: dict[str, Any],
    *,
    conteiner_catalogo_id: int,
    tipo_conteudo: str,
) -> ConteudoConteinerCatalogoDTO:
    """
    Normaliza um conteúdo de contêiner da CSGO-API.

    O identificador interno do contêiner deve ser
    previamente resolvido pela camada de serviço.
    """

    if not isinstance(registro, dict):
        raise ErroNormalizacaoConteudoCSGOAPI(
            "Registro de conteúdo inválido."
        )

    if (
        not isinstance(conteiner_catalogo_id, int)
        or isinstance(conteiner_catalogo_id, bool)
        or conteiner_catalogo_id <= 0
    ):
        raise ErroNormalizacaoConteudoCSGOAPI(
            "ID do contêiner inválido."
        )

    tipo_normalizado = _obter_texto(
        tipo_conteudo
    )

    if tipo_normalizado not in TIPOS_CONTEUDOS_CSGO_API:
        raise ErroNormalizacaoConteudoCSGOAPI(
            "Tipo de conteúdo não suportado."
        )

    id_externo = _obter_texto(
        registro.get("id")
    )

    if id_externo is None:
        raise ErroNormalizacaoConteudoCSGOAPI(
            "Conteúdo sem ID externo válido."
        )

    if len(id_externo) > 150:
        raise ErroNormalizacaoConteudoCSGOAPI(
            "ID externo do conteúdo excede 150 caracteres."
        )

    nome = _obter_texto(
        registro.get("name")
    )

    if nome is None:
        raise ErroNormalizacaoConteudoCSGOAPI(
            "Conteúdo sem nome válido."
        )

    if len(nome) > 255:
        raise ErroNormalizacaoConteudoCSGOAPI(
            "Nome do conteúdo excede 255 caracteres."
        )

    raridade_origem = registro.get("rarity")

    raridade = _obter_nome_objeto(
        raridade_origem
    )

    if raridade is not None and len(raridade) > 100:
        raise ErroNormalizacaoConteudoCSGOAPI(
            "Raridade do conteúdo excede 100 caracteres."
        )

    indice_pintura = _obter_indice_pintura(
        registro.get("paint_index")
    )

    fase_origem = registro.get("phase")

    if isinstance(fase_origem, dict):
        nome_fase = _obter_nome_objeto(
            fase_origem
        )
    else:
        nome_fase = _obter_texto(
            fase_origem
        )

    if nome_fase is not None and len(nome_fase) > 100:
        raise ErroNormalizacaoConteudoCSGOAPI(
            "Fase do conteúdo excede 100 caracteres."
        )

    url_imagem = _obter_texto(
        registro.get("image")
    )

    return ConteudoConteinerCatalogoDTO(
        conteiner_catalogo_id=conteiner_catalogo_id,
        fonte=FONTE_CSGO_API,
        id_externo_conteudo=id_externo,
        nome_conteudo=nome,
        tipo_conteudo=tipo_normalizado,
        raridade=raridade,
        indice_pintura=indice_pintura,
        nome_fase=nome_fase,
        url_imagem=url_imagem,
    )