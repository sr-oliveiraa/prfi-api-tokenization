"""
Módulo de tokenização PRFIC para o protocolo PRFI.

Este módulo implementa o sistema de tokenização que gera 1 PRFIC
a cada 1.000 eventos processados, distribuindo 80% para a empresa
e 20% para o desenvolvedor.
"""

from .contador import EventCounter, CompanyEventCounter
from .modelos import Company, TokenBatch, EventLedger
from .blockchain import BlockchainGateway, PRFICContract
from .servicos import TokenizationService

__all__ = [
    "EventCounter",
    "CompanyEventCounter", 
    "Company",
    "TokenBatch",
    "EventLedger",
    "BlockchainGateway",
    "PRFICContract",
    "TokenizationService",
]
