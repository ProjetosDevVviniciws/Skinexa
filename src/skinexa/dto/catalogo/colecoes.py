from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class ColecaoCatalogoDTO:
    """Representa uma coleção normalizada de uma fonte externa."""

    fonte: str
    id_externo: str
    nome: str

    tipo_colecao: str | None = None
    url_imagem: str | None = None

@dataclass(frozen=True, slots=True)
class RelacaoItemColecaoDTO:
    """Representa o vínculo entre um item comercial e uma coleção."""

    item_catalogo_id: int
    colecao_catalogo_id: int
    fonte_relacao: str