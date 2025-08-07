"""
Modelos de dados para o sistema de tokenização PRFIC.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TokenBatchStatus(str, Enum):
    """Status possíveis de um lote de tokens."""
    PENDING = "pending"
    PROCESSING = "processing"
    MINTED = "minted"
    FAILED = "failed"


class Company(BaseModel):
    """Modelo de empresa no sistema PRFI."""
    id: str = Field(..., description="ID único da empresa")
    name: str = Field(..., description="Nome da empresa")
    wallet_address: Optional[str] = Field(None, description="Endereço da wallet Polygon")
    api_key: str = Field(..., description="Chave API para autenticação")
    secret_key: str = Field(..., description="Chave secreta HMAC")
    
    # Configurações de tokenização
    events_per_token: int = Field(default=1000, description="Eventos necessários para 1 PRFIC")
    auto_mint: bool = Field(default=True, description="Mint automático ao atingir threshold")
    
    # Contadores
    total_events: int = Field(default=0, description="Total de eventos processados")
    current_batch_events: int = Field(default=0, description="Eventos no lote atual")
    total_tokens_earned: float = Field(default=0.0, description="Total de tokens ganhos")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TokenBatch(BaseModel):
    """Modelo de lote de tokens para mint."""
    id: str = Field(default_factory=lambda: str(uuid4()), description="ID único do lote")
    company_id: str = Field(..., description="ID da empresa")
    
    # Dados do lote
    events_count: int = Field(default=1000, description="Número de eventos no lote")
    batch_hash: str = Field(..., description="Hash do lote para auditoria")
    
    # Tokenização
    tokens_to_mint: float = Field(default=1.0, description="Quantidade de PRFIC a ser mintada")
    company_tokens: float = Field(default=0.8, description="Tokens para a empresa (80%)")
    developer_tokens: float = Field(default=0.2, description="Tokens para o desenvolvedor (20%)")
    
    # Blockchain
    blockchain_tx_hash: Optional[str] = Field(None, description="Hash da transação na blockchain")
    block_number: Optional[int] = Field(None, description="Número do bloco")
    gas_used: Optional[int] = Field(None, description="Gas usado na transação")
    
    # Status e controle
    status: TokenBatchStatus = Field(default=TokenBatchStatus.PENDING)
    error_message: Optional[str] = Field(None, description="Mensagem de erro se houver")
    retry_count: int = Field(default=0, description="Número de tentativas de mint")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = Field(None, description="Quando foi processado")
    minted_at: Optional[datetime] = Field(None, description="Quando foi mintado")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EventLedger(BaseModel):
    """Registro de auditoria para eventos processados."""
    id: str = Field(default_factory=lambda: str(uuid4()), description="ID único do registro")
    
    # Referências
    event_id: str = Field(..., description="ID do evento PRFI")
    company_id: str = Field(..., description="ID da empresa")
    batch_id: Optional[str] = Field(None, description="ID do lote de tokens")
    
    # Dados de auditoria
    ip_address: Optional[str] = Field(None, description="IP de origem do evento")
    user_agent: Optional[str] = Field(None, description="User agent do cliente")
    event_type: str = Field(..., description="Tipo do evento")
    url: str = Field(..., description="URL de destino")
    
    # Metadados
    payload_hash: str = Field(..., description="Hash do payload para integridade")
    signature: Optional[str] = Field(None, description="Assinatura HMAC")
    
    # Timestamps
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TokenizationMetrics(BaseModel):
    """Métricas de tokenização para dashboard."""
    company_id: str
    
    # Contadores
    total_events: int = 0
    events_this_month: int = 0
    current_batch_progress: int = 0
    
    # Tokens
    total_tokens_earned: float = 0.0
    tokens_this_month: float = 0.0
    pending_tokens: float = 0.0
    
    # Lotes
    total_batches: int = 0
    successful_batches: int = 0
    failed_batches: int = 0
    
    # Taxas
    success_rate: float = 0.0
    average_batch_time: float = 0.0
    
    # Timestamps
    last_token_mint: Optional[datetime] = None
    next_estimated_mint: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
