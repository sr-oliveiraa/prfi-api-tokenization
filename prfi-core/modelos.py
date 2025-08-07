"""
Modelos de dados para o protocolo PRFI.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class EventStatus(str, Enum):
    """Status possíveis de um evento PRFI."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


class StorageType(str, Enum):
    """Tipos de storage suportados."""
    SQLITE = "sqlite"
    REDIS = "redis"
    MEMORY = "memory"


class PRFIEvent(BaseModel):
    """
    Modelo principal do evento PRFI.
    
    Representa um evento que será enviado com retry automático.
    """
    # Campos obrigatórios do protocolo PRFI
    prfi_event_id: UUID = Field(default_factory=uuid4, description="ID único do evento")
    prfi_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp de criação")
    prfi_attempts: int = Field(default=0, description="Número de tentativas realizadas")
    prfi_max_attempts: int = Field(default=5, description="Máximo de tentativas permitidas")
    prfi_signature: Optional[str] = Field(None, description="Assinatura HMAC do payload")
    prfi_nonce: Optional[str] = Field(None, description="Nonce para segurança")
    
    # Metadados do evento
    event_type: str = Field(..., description="Tipo do evento (ex: payment.completed)")
    url: str = Field(..., description="URL de destino para envio")
    method: str = Field(default="POST", description="Método HTTP")
    headers: Dict[str, str] = Field(default_factory=dict, description="Headers HTTP adicionais")
    
    # Dados do evento
    data: Dict[str, Any] = Field(..., description="Payload do evento")
    
    # Status e controle
    status: EventStatus = Field(default=EventStatus.PENDING, description="Status atual do evento")
    last_attempt_at: Optional[datetime] = Field(None, description="Timestamp da última tentativa")
    next_attempt_at: Optional[datetime] = Field(None, description="Timestamp da próxima tentativa")
    error_message: Optional[str] = Field(None, description="Mensagem do último erro")
    
    # Configuração de retry específica do evento
    initial_delay: float = Field(default=1.0, description="Delay inicial em segundos")
    max_delay: float = Field(default=300.0, description="Delay máximo em segundos")
    multiplier: float = Field(default=2.0, description="Multiplicador do backoff")
    jitter: bool = Field(default=True, description="Adicionar jitter ao delay")

    @validator('prfi_event_id', pre=True)
    def validate_event_id(cls, v):
        if isinstance(v, str):
            return UUID(v)
        return v

    @validator('method')
    def validate_method(cls, v):
        allowed_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
        if v.upper() not in allowed_methods:
            raise ValueError(f'Método {v} não permitido. Use: {allowed_methods}')
        return v.upper()

    def to_payload(self) -> Dict[str, Any]:
        """Converte o evento para o payload que será enviado."""
        return {
            "prfi_event_id": str(self.prfi_event_id),
            "prfi_timestamp": self.prfi_timestamp.isoformat(),
            "prfi_attempts": self.prfi_attempts,
            "prfi_max_attempts": self.prfi_max_attempts,
            "prfi_signature": self.prfi_signature,
            "prfi_nonce": self.prfi_nonce,
            "event_type": self.event_type,
            "data": self.data
        }

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class RetryConfig(BaseModel):
    """Configuração de retry para o cliente PRFI."""
    initial_delay: float = Field(default=1.0, ge=0.1, description="Delay inicial em segundos")
    max_delay: float = Field(default=300.0, ge=1.0, description="Delay máximo em segundos")
    multiplier: float = Field(default=2.0, ge=1.0, description="Multiplicador do backoff")
    jitter: bool = Field(default=True, description="Adicionar jitter ao delay")
    max_attempts: int = Field(default=5, ge=1, le=20, description="Máximo de tentativas")

    @validator('max_delay')
    def validate_max_delay(cls, v, values):
        if 'initial_delay' in values and v < values['initial_delay']:
            raise ValueError('max_delay deve ser maior que initial_delay')
        return v


class StorageConfig(BaseModel):
    """Configuração base para storage."""
    type: StorageType
    
    class Config:
        extra = "allow"  # Permite campos adicionais específicos do storage


class SQLiteConfig(StorageConfig):
    """Configuração específica para SQLite."""
    type: StorageType = StorageType.SQLITE
    path: str = Field(default="./prfi.db", description="Caminho do arquivo SQLite")
    timeout: float = Field(default=30.0, description="Timeout para operações")


class RedisConfig(StorageConfig):
    """Configuração específica para Redis."""
    type: StorageType = StorageType.REDIS
    host: str = Field(default="localhost", description="Host do Redis")
    port: int = Field(default=6379, description="Porta do Redis")
    db: int = Field(default=0, description="Número do banco Redis")
    password: Optional[str] = Field(None, description="Senha do Redis")
    ssl: bool = Field(default=False, description="Usar SSL")
    timeout: float = Field(default=30.0, description="Timeout para operações")


class PRFIConfig(BaseModel):
    """Configuração principal do cliente PRFI."""
    secret_key: str = Field(..., description="Chave secreta para assinatura HMAC")
    storage: Union[SQLiteConfig, RedisConfig] = Field(..., description="Configuração de storage")
    retry: RetryConfig = Field(default_factory=RetryConfig, description="Configuração de retry")
    
    # Configurações de segurança
    verify_signatures: bool = Field(default=True, description="Verificar assinaturas HMAC")
    require_https: bool = Field(default=True, description="Exigir HTTPS para URLs")
    
    # Configurações de performance
    max_concurrent_requests: int = Field(default=10, ge=1, le=100, description="Máximo de requests simultâneos")
    request_timeout: float = Field(default=30.0, ge=1.0, description="Timeout para requests HTTP")
    
    # Configurações de monitoramento
    enable_metrics: bool = Field(default=True, description="Habilitar métricas")
    log_level: str = Field(default="INFO", description="Nível de log")

    @validator('secret_key')
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError('secret_key deve ter pelo menos 32 caracteres')
        return v

    @validator('log_level')
    def validate_log_level(cls, v):
        allowed_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed_levels:
            raise ValueError(f'log_level deve ser um de: {allowed_levels}')
        return v.upper()


class PRFIResponse(BaseModel):
    """Resposta padrão da API PRFI."""
    success: bool = Field(..., description="Se a operação foi bem-sucedida")
    message: str = Field(..., description="Mensagem descritiva")
    event_id: Optional[UUID] = Field(None, description="ID do evento relacionado")
    data: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp da resposta")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class EventListResponse(BaseModel):
    """Resposta para listagem de eventos."""
    events: list[PRFIEvent] = Field(..., description="Lista de eventos")
    total: int = Field(..., description="Total de eventos")
    page: int = Field(default=1, description="Página atual")
    per_page: int = Field(default=50, description="Eventos por página")
    has_next: bool = Field(..., description="Se há próxima página")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
