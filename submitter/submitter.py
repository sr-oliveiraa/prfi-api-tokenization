"""
Submitter principal para blockchain.

Responsável por:
- Coordenar todo o processo de submissão
- Gerenciar conexão com blockchain
- Executar transações no smart contract
- Monitorar confirmações
- Implementar retry automático
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

import structlog
from web3 import Web3
from web3.middleware import geth_poa_middleware

from minerador.models import MiningBlock, BlockStatus
from minerador.storage import LocalBlockStorage
from .models import (
    SubmissionConfig, SubmissionBatch, SubmissionResult, 
    BatchStatus, SubmissionStats
)
from .scanner import BlockScanner
from .validator import SubmissionValidator
from .batcher import BlockBatcher
from .monitor import SubmissionMonitor
from .gas_optimizer import GasOptimizer

logger = structlog.get_logger(__name__)


class BlockSubmitter:
    """Submitter principal de blocos para blockchain."""
    
    def __init__(self, config: SubmissionConfig):
        """
        Inicializa o submitter.
        
        Args:
            config: Configuração do sistema de submissão
        """
        self.config = config
        self.logger = logger.bind(component="block_submitter")
        
        # Inicializar componentes
        self.scanner = BlockScanner(config)
        self.validator = SubmissionValidator(config)
        self.batcher = BlockBatcher(config)
        self.storage = LocalBlockStorage(config.blocks_directory)
        
        # Inicializar Web3
        self.w3 = self._setup_web3()
        self.contract = self._setup_contract()
        
        # Componentes opcionais
        self.monitor: Optional[SubmissionMonitor] = None
        self.gas_optimizer: Optional[GasOptimizer] = None
        
        # Estatísticas
        self.stats = SubmissionStats()
        
        # Estado interno
        self._running = False
        self._pending_batches: List[SubmissionBatch] = []
        
        self.logger.info("Block submitter inicializado")
    
    def _setup_web3(self) -> Web3:
        """Configura conexão Web3 com a blockchain."""
        try:
            w3 = Web3(Web3.HTTPProvider(self.config.rpc_url))
            
            # Adicionar middleware para Polygon (PoA)
            if self.config.chain_id == 137:  # Polygon mainnet
                w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            
            # Verificar conexão
            if not w3.is_connected():
                raise ConnectionError("Não foi possível conectar à blockchain")
            
            # Configurar conta
            account = w3.eth.account.from_key(self.config.private_key)
            w3.eth.default_account = account.address
            
            self.logger.info(
                "Web3 configurado",
                chain_id=self.config.chain_id,
                account=account.address,
                latest_block=w3.eth.block_number
            )
            
            return w3
            
        except Exception as e:
            self.logger.error(
                "Erro ao configurar Web3",
                error=str(e)
            )
            raise
    
    def _setup_contract(self):
        """Configura interface do smart contract."""
        try:
            # ABI simplificado do contrato PRFIC
            contract_abi = [
                {
                    "inputs": [
                        {"name": "batchId", "type": "string"},
                        {"name": "blockIds", "type": "string[]"},
                        {"name": "miners", "type": "address[]"},
                        {"name": "points", "type": "uint256[]"},
                        {"name": "signatures", "type": "bytes[]"}
                    ],
                    "name": "submitBlocks",
                    "outputs": [{"name": "", "type": "bool"}],
                    "stateMutability": "nonpayable",
                    "type": "function"
                },
                {
                    "inputs": [{"name": "batchId", "type": "string"}],
                    "name": "getBatchStatus",
                    "outputs": [{"name": "", "type": "bool"}],
                    "stateMutability": "view",
                    "type": "function"
                }
            ]
            
            contract = self.w3.eth.contract(
                address=self.config.contract_address,
                abi=contract_abi
            )
            
            self.logger.info(
                "Contrato configurado",
                address=self.config.contract_address
            )
            
            return contract
            
        except Exception as e:
            self.logger.error(
                "Erro ao configurar contrato",
                error=str(e)
            )
            raise
    
    async def process_pending_blocks(self) -> List[SubmissionResult]:
        """
        Processa todos os blocos pendentes de submissão.
        
        Returns:
            Lista de resultados das submissões
        """
        self.logger.info("Iniciando processamento de blocos pendentes")
        
        try:
            # 1. Escanear blocos pendentes
            pending_blocks = self.scanner.scan_pending_blocks()
            
            if not pending_blocks:
                self.logger.info("Nenhum bloco pendente encontrado")
                return []
            
            # 2. Validar blocos
            valid_blocks, validation_errors = self.validator.validate_blocks(pending_blocks)
            
            if validation_errors:
                self.logger.warning(
                    "Erros de validação encontrados",
                    errors_count=len(validation_errors),
                    errors=validation_errors[:5]  # Mostrar apenas os primeiros 5
                )
            
            if not valid_blocks:
                self.logger.warning("Nenhum bloco válido para submissão")
                return []
            
            # 3. Criar batches
            batches = self.batcher.create_batches(valid_blocks)
            
            if not batches:
                self.logger.warning("Nenhum batch criado")
                return []
            
            # 4. Submeter batches
            results = []
            for batch in batches:
                result = await self.submit_batch(batch)
                results.append(result)
                
                # Delay entre submissões para evitar nonce conflicts
                if len(batches) > 1:
                    await asyncio.sleep(2)
            
            self.logger.info(
                "Processamento concluído",
                total_blocks=len(pending_blocks),
                valid_blocks=len(valid_blocks),
                batches_created=len(batches),
                successful_submissions=sum(1 for r in results if r.success)
            )
            
            return results
            
        except Exception as e:
            self.logger.error(
                "Erro no processamento de blocos pendentes",
                error=str(e)
            )
            return []
    
    async def submit_batch(self, batch: SubmissionBatch) -> SubmissionResult:
        """
        Submete um batch para a blockchain.
        
        Args:
            batch: Batch para submeter
            
        Returns:
            Resultado da submissão
        """
        self.logger.info(
            "Submetendo batch",
            batch_id=batch.batch_id,
            blocks_count=len(batch.blocks),
            total_points=batch.total_points
        )
        
        try:
            # Atualizar status do batch
            batch.status = BatchStatus.SUBMITTING
            batch.submitted_at = datetime.utcnow()
            
            # Preparar dados para o contrato
            contract_data = self.validator.prepare_for_submission(batch.blocks)
            
            # Estimar gas
            gas_estimate = await self._estimate_gas(contract_data)
            
            # Executar transação
            tx_hash = await self._execute_transaction(contract_data, gas_estimate)
            
            # Atualizar batch com dados da transação
            batch.tx_hash = tx_hash
            batch.status = BatchStatus.SUBMITTED
            
            # Atualizar status dos blocos
            for block in batch.blocks:
                self.storage.update_block_status(
                    block.block_id,
                    BlockStatus.SUBMITTED,
                    tx_hash
                )
            
            self.logger.info(
                "Batch submetido com sucesso",
                batch_id=batch.batch_id,
                tx_hash=tx_hash
            )
            
            return SubmissionResult(
                success=True,
                batch_id=batch.batch_id,
                tx_hash=tx_hash,
                blocks_submitted=len(batch.blocks),
                points_submitted=batch.total_points,
                gas_used=gas_estimate
            )
            
        except Exception as e:
            # Atualizar status de erro
            batch.status = BatchStatus.FAILED
            batch.last_error = str(e)
            batch.retry_count += 1
            
            # Agendar retry se possível
            retry_scheduled = False
            if batch.can_retry:
                self._pending_batches.append(batch)
                retry_scheduled = True
            
            self.logger.error(
                "Erro na submissão do batch",
                batch_id=batch.batch_id,
                error=str(e),
                retry_count=batch.retry_count,
                retry_scheduled=retry_scheduled
            )
            
            return SubmissionResult(
                success=False,
                batch_id=batch.batch_id,
                error=str(e),
                retry_scheduled=retry_scheduled
            )
    
    async def _estimate_gas(self, contract_data: Dict[str, Any]) -> int:
        """Estima gas necessário para a transação."""
        try:
            # Estimar gas usando o contrato
            gas_estimate = self.contract.functions.submitBlocks(
                contract_data["batch_id"],
                contract_data["block_ids"],
                contract_data["miners"],
                contract_data["points"],
                contract_data["signatures"]
            ).estimate_gas()
            
            # Adicionar margem de segurança (20%)
            gas_with_margin = int(gas_estimate * 1.2)
            
            # Aplicar limite máximo
            final_gas = min(gas_with_margin, self.config.gas_limit)
            
            self.logger.debug(
                "Gas estimado",
                estimated=gas_estimate,
                with_margin=gas_with_margin,
                final=final_gas
            )
            
            return final_gas
            
        except Exception as e:
            self.logger.warning(
                "Erro na estimativa de gas, usando padrão",
                error=str(e),
                default_gas=self.config.gas_limit
            )
            return self.config.gas_limit
    
    async def _execute_transaction(self, contract_data: Dict[str, Any], gas_limit: int) -> str:
        """Executa a transação no smart contract."""
        try:
            # Obter preço do gas
            gas_price = self.w3.eth.gas_price
            max_gas_price = min(
                int(gas_price * self.config.gas_price_multiplier),
                self.config.max_gas_price
            )
            
            # Obter nonce
            nonce = self.w3.eth.get_transaction_count(self.w3.eth.default_account)
            
            # Construir transação
            transaction = self.contract.functions.submitBlocks(
                contract_data["batch_id"],
                contract_data["block_ids"],
                contract_data["miners"],
                contract_data["points"],
                contract_data["signatures"]
            ).build_transaction({
                'gas': gas_limit,
                'gasPrice': max_gas_price,
                'nonce': nonce,
                'chainId': self.config.chain_id
            })
            
            # Assinar transação
            account = self.w3.eth.account.from_key(self.config.private_key)
            signed_txn = account.sign_transaction(transaction)
            
            # Enviar transação
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            self.logger.info(
                "Transação enviada",
                tx_hash=tx_hash.hex(),
                gas_limit=gas_limit,
                gas_price=max_gas_price,
                nonce=nonce
            )
            
            return tx_hash.hex()
            
        except Exception as e:
            self.logger.error(
                "Erro na execução da transação",
                error=str(e)
            )
            raise
    
    async def monitor_confirmations(self) -> None:
        """Monitora confirmações de transações pendentes."""
        if not self.monitor:
            self.monitor = SubmissionMonitor(self.config, self.w3)
        
        await self.monitor.monitor_pending_transactions()
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do submitter."""
        scanner_stats = self.scanner.get_scan_stats()
        validator_stats = self.validator.get_validation_stats()
        
        return {
            "submitter": {
                "running": self._running,
                "pending_batches": len(self._pending_batches),
                "stats": self.stats.dict()
            },
            "scanner": scanner_stats,
            "validator": validator_stats,
            "blockchain": {
                "connected": self.w3.is_connected(),
                "latest_block": self.w3.eth.block_number,
                "account": self.w3.eth.default_account,
                "balance": self.w3.eth.get_balance(self.w3.eth.default_account)
            }
        }
    
    async def start_continuous_processing(self, interval: int = 60) -> None:
        """
        Inicia processamento contínuo de blocos.
        
        Args:
            interval: Intervalo entre processamentos (segundos)
        """
        self._running = True
        self.logger.info(
            "Iniciando processamento contínuo",
            interval=interval
        )
        
        while self._running:
            try:
                # Processar blocos pendentes
                await self.process_pending_blocks()
                
                # Processar retries
                await self._process_retries()
                
                # Monitorar confirmações
                await self.monitor_confirmations()
                
                # Aguardar próximo ciclo
                await asyncio.sleep(interval)
                
            except Exception as e:
                self.logger.error(
                    "Erro no processamento contínuo",
                    error=str(e)
                )
                await asyncio.sleep(interval)
    
    def stop_continuous_processing(self) -> None:
        """Para o processamento contínuo."""
        self._running = False
        self.logger.info("Processamento contínuo parado")
    
    async def _process_retries(self) -> None:
        """Processa batches que precisam de retry."""
        if not self._pending_batches:
            return
        
        retry_batches = []
        for batch in self._pending_batches:
            if batch.can_retry:
                # Verificar se já passou o tempo de delay
                if batch.submitted_at:
                    delay = timedelta(seconds=self.config.retry_delay)
                    if self.config.exponential_backoff:
                        delay *= (2 ** batch.retry_count)
                    
                    if datetime.utcnow() - batch.submitted_at >= delay:
                        retry_batches.append(batch)
        
        # Remover batches que serão reprocessados
        for batch in retry_batches:
            self._pending_batches.remove(batch)
        
        # Reprocessar batches
        for batch in retry_batches:
            batch.status = BatchStatus.RETRY
            result = await self.submit_batch(batch)
            
            if not result.success and not result.retry_scheduled:
                # Falha final, atualizar blocos
                for block in batch.blocks:
                    self.storage.update_block_status(
                        block.block_id,
                        BlockStatus.FAILED
                    )
