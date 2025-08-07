"""
Modelos de dados para o sistema de mineração PRFI
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from uuid import uuid4


class BlockStatus(str, Enum):
    """Status possíveis de um bloco"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    CONFIRMED = "confirmed"
    FAILED = "failed"


@dataclass
class MiningBlock:
    """Bloco minerado com dados de evento"""
    # Identificação
    block_id: str = field(default_factory=lambda: str(uuid4()))
    event_id: str = ""
    
    # Dados do evento
    status: int = 200
    retries: int = 0
    fallback_used: bool = False
    source_system: str = ""
    destination: str = ""
    
    # Mineração
    points: float = 0.0
    miner: str = ""
    signature: str = ""
    public_key: str = ""
    payload_hash: str = ""
    
    # Métricas
    request_duration: float = 0.0
    response_size: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    mined_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    
    # Status
    block_status: BlockStatus = BlockStatus.PENDING
    tx_hash: Optional[str] = None
    confirmation_block: Optional[int] = None
    
    def get_signing_data(self) -> str:
        """Obtém dados para assinatura digital"""
        return f"{self.block_id}{self.event_id}{self.status}{self.points}{self.miner}{self.payload_hash}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'block_id': self.block_id,
            'event_id': self.event_id,
            'status': self.status,
            'retries': self.retries,
            'fallback_used': self.fallback_used,
            'source_system': self.source_system,
            'destination': self.destination,
            'points': self.points,
            'miner': self.miner,
            'signature': self.signature,
            'public_key': self.public_key,
            'payload_hash': self.payload_hash,
            'request_duration': self.request_duration,
            'response_size': self.response_size,
            'created_at': self.created_at.isoformat(),
            'mined_at': self.mined_at.isoformat() if self.mined_at else None,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'block_status': self.block_status.value,
            'tx_hash': self.tx_hash,
            'confirmation_block': self.confirmation_block
        }


@dataclass
class MiningResult:
    """Resultado de uma operação de mineração"""
    success: bool
    block: Optional[MiningBlock] = None
    points_earned: float = 0.0
    error: Optional[str] = None
    validation_errors: Optional[list] = None
    mining_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'success': self.success,
            'block': self.block.to_dict() if self.block else None,
            'points_earned': self.points_earned,
            'error': self.error,
            'validation_errors': self.validation_errors,
            'mining_time': self.mining_time
        }


@dataclass
class MinerConfig:
    """Configuração do minerador"""
    # Identificação
    miner_id: str
    miner_address: str
    
    # Chaves
    private_key_path: str
    public_key_path: str
    
    # Diretórios
    blocks_directory: str = "./blocos"
    backup_enabled: bool = True
    
    # Limites de mineração
    base_points: float = 0.4
    min_points_per_block: float = 0.1
    max_points_per_block: float = 1.0
    max_blocks_per_hour: int = 100
    max_blocks_per_day: int = 1000
    
    # Validação
    min_request_duration: float = 0.1
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'miner_id': self.miner_id,
            'miner_address': self.miner_address,
            'private_key_path': self.private_key_path,
            'public_key_path': self.public_key_path,
            'blocks_directory': self.blocks_directory,
            'backup_enabled': self.backup_enabled,
            'base_points': self.base_points,
            'min_points_per_block': self.min_points_per_block,
            'max_points_per_block': self.max_points_per_block,
            'max_blocks_per_hour': self.max_blocks_per_hour,
            'max_blocks_per_day': self.max_blocks_per_day,
            'min_request_duration': self.min_request_duration
        }


@dataclass
class AntifraudRules:
    """Regras de validação anti-fraude"""
    max_events_per_hour: int = 100
    max_events_per_day: int = 1000
    min_request_duration: float = 0.1
    max_points_per_event: float = 1.0


# Alias para compatibilidade
PRFIMiner = MiningBlock
