from html.parser import HTMLParser

from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class AdesivoSteamExtraido:
    """Representa um adesivo extraído do HTML da Steam."""

    nome_exibicao: str
    url_icone: str | None

class ParserAdesivosSteam(HTMLParser):
    """Extrai adesivos do HTML retornado pela Steam."""

    def __init__(self) -> None:
        super().__init__()

        self.adesivos: list[AdesivoSteamExtraido] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        """Processa tags HTML de abertura."""
        
        if tag.casefold() != "img":
            return

        atributos = dict(attrs)

        titulo = _normalizar_texto(
            atributos.get("title")
        )

        url_icone = _normalizar_texto(
            atributos.get("src")
        )

        if not titulo:
            return

        if not titulo.casefold().startswith(
            "adesivo:"
        ):
            return

        nome_exibicao = titulo.split(
            ":",
            1,
        )[1].strip()

        if not nome_exibicao:
            return

        self.adesivos.append(
            AdesivoSteamExtraido(
                nome_exibicao=nome_exibicao,
                url_icone=url_icone,
            )
        )

def _normalizar_texto(
    valor: str | None,
) -> str | None:
    """Normaliza valores textuais encontrados no HTML."""

    if valor is None:
        return None

    texto = valor.strip()

    return texto or None