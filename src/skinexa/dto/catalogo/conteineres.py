from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class ConteinerCatalogoDTO:
    """Representa um contêiner normalizado de uma fonte externa."""

    fonte: str
    id_externo: str
    nome: str

    item_catalogo_id: int | None = None
    tipo_conteiner: str | None = None
    url_imagem: str | None = None

@dataclass(frozen=True, slots=True)
class ConteudoConteinerCatalogoDTO:
    """Representa um conteúdo associado a um contêiner."""

    conteiner_catalogo_id: int
    fonte: str
    id_externo_conteudo: str
    nome_conteudo: str
    tipo_conteudo: str

    raridade: str | None = None
    indice_pintura: int | None = None
    nome_fase: str | None = None
    url_imagem: str | None = None