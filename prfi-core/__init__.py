"""
PRFI Core - Módulo principal do protocolo PRFI
"""

from .cliente_descentralizado import PRFIClientDescentralizado
from .modelos import PRFIRequest, PRFIResponse, PRFIEvent, RetryConfig
from .excecoes import PRFIException

# Alias para compatibilidade
PRFIClient = PRFIClientDescentralizado

__version__ = "1.0.0"
__all__ = [
    "PRFIClientDescentralizado",
    "PRFIClient", 
    "PRFIRequest",
    "PRFIResponse",
    "PRFIEvent",
    "RetryConfig",
    "PRFIException"
]
