"""Normalização das coleções fornecidas pela CSGO-API."""

from typing import Any

from skinexa.dto.catalogo.colecoes import (
    ColecaoCatalogoDTO,
)

FONTE_CSGO_API = "csgo_api"

class ErroNormalizacaoColecaoCSGOAPI(ValueError):
    """Representa dados inválidos na normalização de coleções."""

def _obter_texto(
    valor: Any,
) -> str | None:
    """Normaliza um valor textual opcional."""

    if not isinstance(valor, str):
        return None

    texto = valor.strip()

    return texto or None

def normalizar_colecao_csgo_api(
    registro: dict[str, Any],
) -> ColecaoCatalogoDTO:
    """Normaliza uma coleção fornecida pela CSGO-API."""

    if not isinstance(registro, dict):
        raise ErroNormalizacaoColecaoCSGOAPI(
            "Registro de coleção inválido."
        )

    id_externo = _obter_texto(
        registro.get("id")
    )

    if id_externo is None:
        raise ErroNormalizacaoColecaoCSGOAPI(
            "Coleção sem ID externo válido."
        )

    if len(id_externo) > 150:
        raise ErroNormalizacaoColecaoCSGOAPI(
            "ID externo da coleção excede 150 caracteres."
        )

    nome = _obter_texto(
        registro.get("name")
    )

    if nome is None:
        raise ErroNormalizacaoColecaoCSGOAPI(
            "Coleção sem nome válido."
        )

    if len(nome) > 255:
        raise ErroNormalizacaoColecaoCSGOAPI(
            "Nome da coleção excede 255 caracteres."
        )

    url_imagem = _obter_texto(
        registro.get("image")
    )

    return ColecaoCatalogoDTO(
        fonte=FONTE_CSGO_API,
        id_externo=id_externo,
        nome=nome,
        tipo_colecao=None,
        url_imagem=url_imagem,
    )
    
def extrair_skin_ids_colecao_csgo_api(
    registro: dict[str, Any],
) -> set[str]:
    """
    Extrai os identificadores das skins de uma coleção.

    Lê o campo contains fornecido pela CSGO-API e
    retorna os skin_ids como um conjunto sem duplicações.

    Não consulta o banco de dados e não modifica
    o registro original.
    """

    if not isinstance(registro, dict):
        raise ErroNormalizacaoColecaoCSGOAPI(
            "Registro de coleção inválido."
        )

    normalizar_colecao_csgo_api(registro)

    conteudos = registro.get("contains")

    if not isinstance(conteudos, list):
        raise ErroNormalizacaoColecaoCSGOAPI(
            "Relacionamentos da coleção inválidos."
        )

    skin_ids: set[str] = set()

    for indice, conteudo in enumerate(conteudos):
        if not isinstance(conteudo, dict):
            raise ErroNormalizacaoColecaoCSGOAPI(
                "Conteúdo inválido na coleção "
                f"na posição {indice}."
            )

        skin_id = _obter_texto(
            conteudo.get("id")
        )

        if skin_id is None:
            raise ErroNormalizacaoColecaoCSGOAPI(
                "Skin sem identificador válido "
                f"na posição {indice}."
            )

        if len(skin_id) > 150:
            raise ErroNormalizacaoColecaoCSGOAPI(
                "Identificador da skin excede "
                "150 caracteres."
            )

        skin_ids.add(skin_id)

    return skin_ids