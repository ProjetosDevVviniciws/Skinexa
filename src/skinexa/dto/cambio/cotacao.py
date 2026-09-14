from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

@dataclass(frozen=True, slots=True)
class CotacaoCambioDTO:
    """Representa uma cotação de câmbio externa."""

    moeda_origem: str
    moeda_destino: str
    taxa: Decimal
    cotado_em: datetime | None