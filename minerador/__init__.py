"""
Minerador PRFI - Sistema de mineração e proof-of-work
"""

from .miner import BlockMiner, create_block_miner
from .models import MiningBlock, MiningResult, MinerConfig

__version__ = "1.0.0"
__all__ = [
    "BlockMiner",
    "create_block_miner", 
    "MiningBlock",
    "MiningResult",
    "MinerConfig"
]
