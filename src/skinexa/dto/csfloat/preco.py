from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

@dataclass(frozen=True, slots=True)
class PrecoCSFloatDTO:
    """Representa os dados de preço recebidos da CSFloat."""

    market_hash_name: str
    preco: Decimal
    criado_em: datetime | None