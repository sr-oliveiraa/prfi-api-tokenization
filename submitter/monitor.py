"""
Monitor de transações blockchain.

Responsável por:
- Monitorar status de transações pendentes
- Detectar confirmações na blockchain
- Atualizar status dos blocos
- Detectar transações falhadas
- Calcular métricas de performance
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import structlog
from web3 import Web3

from minerador.models import BlockStatus
from minerador.storage import LocalBlockStorage
from .models import SubmissionConfig, BatchStatus

logger = structlog.get_logger(__name__)


class SubmissionMonitor:
    """Monitor de submissões blockchain."""
    
    def __init__(self, config: SubmissionConfig, w3: Web3):
        """
        Inicializa o monitor.
        
        Args:
            config: Configuração do sistema
            w3: Instância Web3 configurada
        """
        self.config = config
        self.w3 = w3
        self.storage = LocalBlockStorage(config.blocks_directory)
        self.logger = logger.bind(component="submission_monitor")
        
        # Cache de transações monitoradas
        self._monitored_txs: Dict[str, Dict[str, Any]] = {}
        
        # Métricas
        self._confirmation_times: List[float] = []
        self._gas_usage: List[int] = []
        
        self.logger.info("Monitor de submissões inicializado")
    
    async def monitor_pending_transactions(self) -> None:
        """Monitora todas as transações pendentes."""
        try:
            # Obter blocos submetidos
            submitted_blocks = self.storage.get_blocks_by_status(BlockStatus.SUBMITTED)
            
            if not submitted_blocks:
                self.logger.debug("Nenhuma transação pendente para monitorar")
                return
            
            # Agrupar por hash de transação
            tx_blocks: Dict[str, List] = {}
            for block in submitted_blocks:
                if block.tx_hash:
                    if block.tx_hash not in tx_blocks:
                        tx_blocks[block.tx_hash] = []
                    tx_blocks[block.tx_hash].append(block)
            
            self.logger.info(
                "Monitorando transações",
                pending_transactions=len(tx_blocks),
                pending_blocks=len(submitted_blocks)
            )
            
            # Monitorar cada transação
            for tx_hash, blocks in tx_blocks.items():
                await self._monitor_transaction(tx_hash, blocks)
                
        except Exception as e:
            self.logger.error(
                "Erro no monitoramento de transações",
                error=str(e)
            )
    
    async def _monitor_transaction(self, tx_hash: str, blocks: List) -> None:
        """
        Monitora uma transação específica.
        
        Args:
            tx_hash: Hash da transação
            blocks: Lista de blocos associados à transação
        """
        try:
            # Verificar se já está sendo monitorada
            if tx_hash in self._monitored_txs:
                monitor_data = self._monitored_txs[tx_hash]
            else:
                monitor_data = {
                    "tx_hash": tx_hash,
                    "blocks": blocks,
                    "start_time": datetime.utcnow(),
                    "last_check": None,
                    "confirmations": 0,
                    "status": "pending"
                }
                self._monitored_txs[tx_hash] = monitor_data
            
            # Obter receipt da transação
            try:
                receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                
                if receipt:
                    await self._process_transaction_receipt(tx_hash, receipt, blocks)
                else:
                    # Transação ainda pendente
                    await self._check_transaction_timeout(tx_hash, monitor_data)
                    
            except Exception as receipt_error:
                # Transação pode ainda não ter sido minerada
                self.logger.debug(
                    "Transação ainda não minerada",
                    tx_hash=tx_hash,
                    error=str(receipt_error)
                )
                await self._check_transaction_timeout(tx_hash, monitor_data)
            
            # Atualizar timestamp da última verificação
            monitor_data["last_check"] = datetime.utcnow()
            
        except Exception as e:
            self.logger.error(
                "Erro no monitoramento da transação",
                tx_hash=tx_hash,
                error=str(e)
            )
    
    async def _process_transaction_receipt(self, tx_hash: str, receipt: Dict, blocks: List) -> None:
        """
        Processa o receipt de uma transação.
        
        Args:
            tx_hash: Hash da transação
            receipt: Receipt da transação
            blocks: Lista de blocos associados
        """
        try:
            current_block = self.w3.eth.block_number
            confirmations = current_block - receipt.blockNumber
            
            self.logger.debug(
                "Receipt processado",
                tx_hash=tx_hash,
                block_number=receipt.blockNumber,
                confirmations=confirmations,
                gas_used=receipt.gasUsed,
                status=receipt.status
            )
            
            # Verificar se a transação foi bem-sucedida
            if receipt.status == 1:  # Sucesso
                if confirmations >= self.config.confirmation_blocks:
                    # Transação confirmada
                    await self._confirm_transaction(tx_hash, receipt, blocks)
                else:
                    # Aguardando mais confirmações
                    self._monitored_txs[tx_hash]["confirmations"] = confirmations
                    self._monitored_txs[tx_hash]["status"] = "confirming"
            else:
                # Transação falhou
                await self._fail_transaction(tx_hash, receipt, blocks)
                
        except Exception as e:
            self.logger.error(
                "Erro no processamento do receipt",
                tx_hash=tx_hash,
                error=str(e)
            )
    
    async def _confirm_transaction(self, tx_hash: str, receipt: Dict, blocks: List) -> None:
        """
        Confirma uma transação bem-sucedida.
        
        Args:
            tx_hash: Hash da transação
            receipt: Receipt da transação
            blocks: Lista de blocos associados
        """
        try:
            self.logger.info(
                "Transação confirmada",
                tx_hash=tx_hash,
                block_number=receipt.blockNumber,
                gas_used=receipt.gasUsed,
                blocks_count=len(blocks)
            )
            
            # Atualizar status dos blocos
            for block in blocks:
                self.storage.update_block_status(
                    block.block_id,
                    BlockStatus.CONFIRMED,
                    tx_hash,
                    {
                        "block_number": receipt.blockNumber,
                        "gas_used": receipt.gasUsed,
                        "confirmed_at": datetime.utcnow().isoformat()
                    }
                )
            
            # Calcular métricas
            if tx_hash in self._monitored_txs:
                monitor_data = self._monitored_txs[tx_hash]
                confirmation_time = (datetime.utcnow() - monitor_data["start_time"]).total_seconds()
                self._confirmation_times.append(confirmation_time)
                self._gas_usage.append(receipt.gasUsed)
                
                # Remover do monitoramento
                del self._monitored_txs[tx_hash]
            
            self.logger.info(
                "Blocos confirmados na blockchain",
                tx_hash=tx_hash,
                confirmed_blocks=len(blocks)
            )
            
        except Exception as e:
            self.logger.error(
                "Erro na confirmação da transação",
                tx_hash=tx_hash,
                error=str(e)
            )
    
    async def _fail_transaction(self, tx_hash: str, receipt: Dict, blocks: List) -> None:
        """
        Processa uma transação que falhou.
        
        Args:
            tx_hash: Hash da transação
            receipt: Receipt da transação
            blocks: Lista de blocos associados
        """
        try:
            self.logger.warning(
                "Transação falhou",
                tx_hash=tx_hash,
                block_number=receipt.blockNumber,
                gas_used=receipt.gasUsed,
                blocks_count=len(blocks)
            )
            
            # Atualizar status dos blocos para pendente (para retry)
            for block in blocks:
                self.storage.update_block_status(
                    block.block_id,
                    BlockStatus.PENDING,  # Voltar para pendente para retry
                    None,
                    {
                        "failed_tx_hash": tx_hash,
                        "failure_reason": "transaction_failed",
                        "failed_at": datetime.utcnow().isoformat()
                    }
                )
            
            # Remover do monitoramento
            if tx_hash in self._monitored_txs:
                del self._monitored_txs[tx_hash]
            
        except Exception as e:
            self.logger.error(
                "Erro no processamento de transação falhada",
                tx_hash=tx_hash,
                error=str(e)
            )
    
    async def _check_transaction_timeout(self, tx_hash: str, monitor_data: Dict) -> None:
        """
        Verifica se uma transação expirou.
        
        Args:
            tx_hash: Hash da transação
            monitor_data: Dados de monitoramento
        """
        try:
            # Verificar timeout (30 minutos)
            timeout = timedelta(minutes=30)
            if datetime.utcnow() - monitor_data["start_time"] > timeout:
                self.logger.warning(
                    "Transação expirou",
                    tx_hash=tx_hash,
                    elapsed_time=(datetime.utcnow() - monitor_data["start_time"]).total_seconds()
                )
                
                # Marcar blocos como pendentes para retry
                for block in monitor_data["blocks"]:
                    self.storage.update_block_status(
                        block.block_id,
                        BlockStatus.PENDING,
                        None,
                        {
                            "timeout_tx_hash": tx_hash,
                            "timeout_reason": "transaction_timeout",
                            "timeout_at": datetime.utcnow().isoformat()
                        }
                    )
                
                # Remover do monitoramento
                del self._monitored_txs[tx_hash]
                
        except Exception as e:
            self.logger.error(
                "Erro na verificação de timeout",
                tx_hash=tx_hash,
                error=str(e)
            )
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do monitoramento."""
        try:
            # Calcular métricas
            avg_confirmation_time = 0.0
            if self._confirmation_times:
                avg_confirmation_time = sum(self._confirmation_times) / len(self._confirmation_times)
            
            avg_gas_usage = 0.0
            if self._gas_usage:
                avg_gas_usage = sum(self._gas_usage) / len(self._gas_usage)
            
            # Status das transações monitoradas
            pending_count = 0
            confirming_count = 0
            
            for monitor_data in self._monitored_txs.values():
                if monitor_data["status"] == "pending":
                    pending_count += 1
                elif monitor_data["status"] == "confirming":
                    confirming_count += 1
            
            return {
                "monitored_transactions": len(self._monitored_txs),
                "pending_transactions": pending_count,
                "confirming_transactions": confirming_count,
                "avg_confirmation_time": avg_confirmation_time,
                "avg_gas_usage": avg_gas_usage,
                "total_confirmations": len(self._confirmation_times),
                "blockchain_height": self.w3.eth.block_number
            }
            
        except Exception as e:
            self.logger.error(
                "Erro ao obter estatísticas",
                error=str(e)
            )
            return {}
    
    def get_transaction_status(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """
        Obtém status de uma transação específica.
        
        Args:
            tx_hash: Hash da transação
            
        Returns:
            Dados de status da transação ou None
        """
        return self._monitored_txs.get(tx_hash)
    
    def clear_old_data(self, max_age_hours: int = 24) -> None:
        """
        Limpa dados antigos do monitor.
        
        Args:
            max_age_hours: Idade máxima dos dados em horas
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            
            # Limpar transações antigas
            old_txs = []
            for tx_hash, monitor_data in self._monitored_txs.items():
                if monitor_data["start_time"] < cutoff_time:
                    old_txs.append(tx_hash)
            
            for tx_hash in old_txs:
                del self._monitored_txs[tx_hash]
            
            # Limpar métricas antigas (manter apenas as últimas 1000)
            if len(self._confirmation_times) > 1000:
                self._confirmation_times = self._confirmation_times[-1000:]
            
            if len(self._gas_usage) > 1000:
                self._gas_usage = self._gas_usage[-1000:]
            
            if old_txs:
                self.logger.info(
                    "Dados antigos limpos",
                    removed_transactions=len(old_txs),
                    max_age_hours=max_age_hours
                )
                
        except Exception as e:
            self.logger.error(
                "Erro na limpeza de dados antigos",
                error=str(e)
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do monitor."""
        try:
            # Verificar conexão blockchain
            latest_block = self.w3.eth.block_number
            is_synced = True  # Simplificado
            
            # Verificar transações pendentes
            pending_count = len(self._monitored_txs)
            
            # Verificar se há transações muito antigas
            old_transactions = 0
            cutoff_time = datetime.utcnow() - timedelta(hours=2)
            
            for monitor_data in self._monitored_txs.values():
                if monitor_data["start_time"] < cutoff_time:
                    old_transactions += 1
            
            return {
                "healthy": True,
                "blockchain_connected": self.w3.is_connected(),
                "latest_block": latest_block,
                "is_synced": is_synced,
                "pending_transactions": pending_count,
                "old_transactions": old_transactions,
                "avg_confirmation_time": sum(self._confirmation_times[-10:]) / min(10, len(self._confirmation_times)) if self._confirmation_times else 0
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "blockchain_connected": False
            }
