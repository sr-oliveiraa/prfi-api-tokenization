"""
Modelos de dados para o sistema de submissão de blocos PRFI.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import uuid4
from pydantic import BaseModel, Field
from enum import Enum

from minerador.models import MiningBlock


class BatchStatus(str, Enum):
    """Status de um batch de submissão."""
    PENDING = "pending"          # Batch criado, aguardando submissão
    SUBMITTING = "submitting"    # Transação sendo enviada
    SUBMITTED = "submitted"      # Transação enviada, aguardando confirmação
    CONFIRMED = "confirmed"      # Transação confirmada na blockchain
    FAILED = "failed"           # Falha na submissão
    RETRY = "retry"             # Aguardando retry após falha


class SubmissionBatch(BaseModel):
    """
    Batch de blocos para submissão em uma única transação.
    
    Agrupa múltiplos blocos para otimizar custos de gas.
    """
    # Identificação
    batch_id: str = Field(default_factory=lambda: str(uuid4()), description="ID único do batch")
    
    # Blocos incluídos
    blocks: List[MiningBlock] = Field(..., description="Blocos incluídos no batch")
    block_ids: List[str] = Field(..., description="IDs dos blocos para referência rápida")
    
    # Dados agregados
    total_points: float = Field(..., description="Total de pontos PRFIC no batch")
    miners: List[str] = Field(..., description="Lista de mineradores únicos")
    
    # Status da submissão
    status: BatchStatus = Field(default=BatchStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = Field(None, description="Timestamp da submissão")
    confirmed_at: Optional[datetime] = Field(None, description="Timestamp da confirmação")
    
    # Dados da blockchain
    tx_hash: Optional[str] = Field(None, description="Hash da transação")
    block_number: Optional[int] = Field(None, description="Número do bloco na blockchain")
    gas_used: Optional[int] = Field(None, description="Gas usado na transação")
    gas_price: Optional[int] = Field(None, description="Preço do gas (wei)")
    
    # Retry e erro
    retry_count: int = Field(default=0, description="Número de tentativas")
    max_retries: int = Field(default=3, description="Máximo de tentativas")
    last_error: Optional[str] = Field(None, description="Último erro ocorrido")
    
    @property
    def can_retry(self) -> bool:
        """Verifica se o batch pode ser reprocessado."""
        return self.retry_count < self.max_retries and self.status in [BatchStatus.FAILED, BatchStatus.RETRY]
    
    @property
    def is_final(self) -> bool:
        """Verifica se o batch está em estado final."""
        return self.status in [BatchStatus.CONFIRMED, BatchStatus.FAILED] and not self.can_retry
    
    def to_contract_data(self) -> Dict[str, Any]:
        """Converte batch para dados do smart contract."""
        return {
            "batch_id": self.batch_id,
            "block_ids": self.block_ids,
            "miners": self.miners,
            "total_points": int(self.total_points * 1000),  # Converter para inteiro (3 decimais)
            "block_count": len(self.blocks)
        }


class SubmissionResult(BaseModel):
    """Resultado de uma operação de submissão."""
    success: bool = Field(..., description="Se a submissão foi bem-sucedida")
    batch_id: str = Field(..., description="ID do batch processado")
    tx_hash: Optional[str] = Field(None, description="Hash da transação")
    blocks_submitted: int = Field(default=0, description="Número de blocos submetidos")
    points_submitted: float = Field(default=0.0, description="Pontos PRFIC submetidos")
    gas_used: Optional[int] = Field(None, description="Gas usado")
    error: Optional[str] = Field(None, description="Mensagem de erro se houver")
    retry_scheduled: bool = Field(default=False, description="Se retry foi agendado")


class SubmissionConfig(BaseModel):
    """Configuração do sistema de submissão."""
    # Blockchain
    rpc_url: str = Field(..., description="URL do RPC da Polygon")
    contract_address: str = Field(..., description="Endereço do contrato PRFIC")
    private_key: str = Field(..., description="Chave privada para submissão")
    chain_id: int = Field(default=137, description="Chain ID da Polygon (137 = mainnet)")
    
    # Batching
    batch_size: int = Field(default=10, description="Número de blocos por batch")
    max_batch_size: int = Field(default=50, description="Tamanho máximo do batch")
    min_batch_size: int = Field(default=1, description="Tamanho mínimo do batch")
    
    # Gas e timing
    gas_limit: int = Field(default=500000, description="Limite de gas por transação")
    gas_price_multiplier: float = Field(default=1.1, description="Multiplicador do preço do gas")
    max_gas_price: int = Field(default=100000000000, description="Preço máximo do gas (100 gwei)")
    
    # Retry
    max_retries: int = Field(default=3, description="Máximo de tentativas por batch")
    retry_delay: int = Field(default=60, description="Delay entre tentativas (segundos)")
    exponential_backoff: bool = Field(default=True, description="Usar backoff exponencial")
    
    # Monitoramento
    confirmation_blocks: int = Field(default=12, description="Blocos para confirmação")
    poll_interval: int = Field(default=30, description="Intervalo de polling (segundos)")
    
    # Diretórios
    blocks_directory: str = Field(default="./blocos", description="Diretório dos blocos")
    logs_directory: str = Field(default="./logs", description="Diretório de logs")
    
    # Otimizações
    enable_gas_optimization: bool = Field(default=True, description="Otimizar preço do gas")
    enable_batch_optimization: bool = Field(default=True, description="Otimizar tamanho dos batches")
    parallel_submissions: int = Field(default=1, description="Submissões paralelas")


class SubmissionStats(BaseModel):
    """Estatísticas do sistema de submissão."""
    # Contadores gerais
    total_batches: int = Field(default=0)
    total_blocks_submitted: int = Field(default=0)
    total_points_submitted: float = Field(default=0.0)
    
    # Status dos batches
    pending_batches: int = Field(default=0)
    submitting_batches: int = Field(default=0)
    submitted_batches: int = Field(default=0)
    confirmed_batches: int = Field(default=0)
    failed_batches: int = Field(default=0)
    retry_batches: int = Field(default=0)
    
    # Métricas de performance
    avg_confirmation_time: float = Field(default=0.0, description="Tempo médio de confirmação (segundos)")
    avg_gas_used: float = Field(default=0.0, description="Gas médio usado")
    avg_gas_price: float = Field(default=0.0, description="Preço médio do gas")
    
    # Custos
    total_gas_used: int = Field(default=0)
    total_cost_wei: int = Field(default=0)
    total_cost_matic: float = Field(default=0.0)
    
    # Timing
    last_submission: Optional[datetime] = Field(None)
    last_confirmation: Optional[datetime] = Field(None)
    uptime_start: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def success_rate(self) -> float:
        """Taxa de sucesso das submissões."""
        total = self.confirmed_batches + self.failed_batches
        if total == 0:
            return 0.0
        return self.confirmed_batches / total
    
    @property
    def avg_batch_size(self) -> float:
        """Tamanho médio dos batches."""
        if self.total_batches == 0:
            return 0.0
        return self.total_blocks_submitted / self.total_batches
    
    def update_from_batch(self, batch: SubmissionBatch) -> None:
        """Atualiza estatísticas com dados de um batch."""
        if batch.status == BatchStatus.CONFIRMED:
            self.confirmed_batches += 1
            self.total_blocks_submitted += len(batch.blocks)
            self.total_points_submitted += batch.total_points
            
            if batch.gas_used:
                self.total_gas_used += batch.gas_used
            
            if batch.gas_price and batch.gas_used:
                cost_wei = batch.gas_price * batch.gas_used
                self.total_cost_wei += cost_wei
                self.total_cost_matic = self.total_cost_wei / 1e18
            
            if batch.confirmed_at:
                self.last_confirmation = batch.confirmed_at
                
                if batch.submitted_at:
                    confirmation_time = (batch.confirmed_at - batch.submitted_at).total_seconds()
                    # Atualizar média móvel
                    if self.avg_confirmation_time == 0:
                        self.avg_confirmation_time = confirmation_time
                    else:
                        self.avg_confirmation_time = (self.avg_confirmation_time * 0.9) + (confirmation_time * 0.1)
        
        elif batch.status == BatchStatus.FAILED:
            self.failed_batches += 1


class GasEstimate(BaseModel):
    """Estimativa de gas para uma transação."""
    estimated_gas: int = Field(..., description="Gas estimado")
    gas_price: int = Field(..., description="Preço do gas recomendado")
    max_fee: int = Field(..., description="Taxa máxima")
    priority_fee: int = Field(..., description="Taxa de prioridade")
    total_cost_wei: int = Field(..., description="Custo total em wei")
    total_cost_matic: float = Field(..., description="Custo total em MATIC")
    
    @property
    def is_affordable(self) -> bool:
        """Verifica se o custo é aceitável (< 0.1 MATIC)."""
        return self.total_cost_matic < 0.1


class BlockchainStatus(BaseModel):
    """Status da blockchain para monitoramento."""
    latest_block: int = Field(..., description="Último bloco")
    gas_price: int = Field(..., description="Preço atual do gas")
    network_congestion: str = Field(..., description="Nível de congestionamento")
    is_healthy: bool = Field(..., description="Se a rede está saudável")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
