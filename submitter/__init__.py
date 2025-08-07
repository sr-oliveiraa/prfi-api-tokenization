"""
Submitter PRFI - Sistema de submissão para blockchain
"""

from .submitter import BlockSubmitter
from .validator import EventValidator
from .gas_optimizer import GasOptimizer

__version__ = "1.0.0"
__all__ = [
    "BlockSubmitter",
    "EventValidator", 
    "GasOptimizer"
]

# Alias para compatibilidade
BlockchainSubmitter = BlockSubmitter
