"""
Serviços de tokenização PRFIC.

Este módulo implementa os serviços de alto nível para gerenciar
o processo completo de tokenização.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any

import structlog

from .contador import CompanyEventCounter
from .modelos import Company, TokenBatch, TokenBatchStatus, TokenizationMetrics
from .adaptador_sqlite import TokenizationSQLiteAdapter
from .blockchain import create_blockchain_from_env, create_prfic_contract, PRFICContract


logger = structlog.get_logger(__name__)


class TokenizationService:
    """Serviço principal de tokenização PRFIC com integração blockchain real."""

    def __init__(
        self,
        storage: TokenizationSQLiteAdapter,
        blockchain_enabled: bool = True,
        prfic_contract: Optional[PRFICContract] = None
    ):
        """
        Inicializa o serviço de tokenização.

        Args:
            storage: Adaptador de storage com suporte a tokenização
            blockchain_enabled: Se deve usar blockchain real ou simulação
            prfic_contract: Contrato PRFIC configurado (opcional)
        """
        self.storage = storage
        self.event_counter = CompanyEventCounter(storage)
        self.logger = logger.bind(component="tokenization_service")

        # Configurações
        self.batch_processing_interval = 30  # segundos
        self.max_retry_attempts = 3
        self.blockchain_enabled = blockchain_enabled

        # Blockchain
        self.prfic_contract = prfic_contract
        if blockchain_enabled and not prfic_contract:
            try:
                # Tentar criar contrato a partir das variáveis de ambiente
                gateway = create_blockchain_from_env()
                self.prfic_contract = create_prfic_contract(gateway)
                self.logger.info("Contrato PRFIC inicializado a partir do ambiente")
            except Exception as e:
                self.logger.warning(
                    "Não foi possível inicializar blockchain, usando simulação",
                    error=str(e)
                )
                self.blockchain_enabled = False

        # Estado interno
        self._processing_task: Optional[asyncio.Task] = None
        self._running = False
    
    async def start(self) -> None:
        """Inicia o serviço de tokenização."""
        if self._running:
            return
        
        self._running = True
        self._processing_task = asyncio.create_task(self._batch_processor())
        
        self.logger.info("Serviço de tokenização iniciado")
    
    async def stop(self) -> None:
        """Para o serviço de tokenização."""
        self._running = False
        
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Serviço de tokenização parado")
    
    async def _batch_processor(self) -> None:
        """Processador de lotes de tokens em background."""
        while self._running:
            try:
                # Buscar lotes pendentes
                pending_batches = await self.storage.get_pending_batches(limit=10)
                
                if pending_batches:
                    self.logger.debug(
                        "Processando lotes pendentes",
                        count=len(pending_batches)
                    )
                    
                    # Processar cada lote
                    for batch in pending_batches:
                        try:
                            await self._process_token_batch(batch)
                        except Exception as e:
                            self.logger.error(
                                "Erro ao processar lote",
                                batch_id=batch.id,
                                error=str(e)
                            )
                
                # Aguardar próximo ciclo
                await asyncio.sleep(self.batch_processing_interval)
                
            except Exception as e:
                self.logger.error(
                    "Erro no processador de lotes",
                    error=str(e)
                )
                await asyncio.sleep(5)
    
    async def _process_token_batch(self, batch: TokenBatch) -> None:
        """Processa um lote de tokens."""
        try:
            # Marcar como processando
            batch.status = TokenBatchStatus.PROCESSING
            batch.processed_at = datetime.utcnow()
            await self.storage.update_token_batch(batch)
            
            self.logger.info(
                "Iniciando processamento de lote",
                batch_id=batch.id,
                company_id=batch.company_id,
                tokens_to_mint=batch.tokens_to_mint
            )
            
            # Processar mint na blockchain (real ou simulado)
            if self.blockchain_enabled and self.prfic_contract:
                success, result = await self._process_blockchain_mint(batch)
            else:
                success, result = await self._simulate_blockchain_mint(batch)

            if success:
                # Marcar como mintado
                batch.status = TokenBatchStatus.MINTED
                batch.minted_at = datetime.utcnow()
                batch.blockchain_tx_hash = result.get("tx_hash")
                batch.block_number = result.get("block_number")
                batch.gas_used = result.get("gas_used")

                # Atualizar tokens da empresa
                await self._update_company_tokens(batch)

                self.logger.info(
                    "Lote processado com sucesso",
                    batch_id=batch.id,
                    company_id=batch.company_id,
                    tx_hash=batch.blockchain_tx_hash,
                    blockchain_enabled=self.blockchain_enabled
                )
            else:
                # Marcar como falhado
                batch.status = TokenBatchStatus.FAILED
                batch.error_message = result.get("error", "Falha no processamento")
                batch.retry_count += 1

                self.logger.error(
                    "Falha ao processar lote",
                    batch_id=batch.id,
                    company_id=batch.company_id,
                    retry_count=batch.retry_count,
                    error=batch.error_message
                )
            
            # Salvar estado atualizado
            await self.storage.update_token_batch(batch)
            
        except Exception as e:
            # Marcar como falhado em caso de erro
            batch.status = TokenBatchStatus.FAILED
            batch.error_message = str(e)
            batch.retry_count += 1
            
            await self.storage.update_token_batch(batch)
            
            self.logger.error(
                "Erro ao processar lote",
                batch_id=batch.id,
                company_id=batch.company_id,
                error=str(e)
            )
    
    async def _process_blockchain_mint(self, batch: TokenBatch) -> tuple[bool, Dict[str, Any]]:
        """Processa mint real na blockchain."""
        try:
            # Obter empresa para pegar o endereço da wallet
            company = await self.storage.get_company(batch.company_id)
            if not company or not company.wallet_address:
                return False, {"error": "Empresa não encontrada ou sem wallet"}

            # Verificar se o lote já foi processado na blockchain
            if await self.prfic_contract.is_batch_processed(batch.id):
                return False, {"error": "Lote já processado na blockchain"}

            # Executar mint na blockchain
            result = await self.prfic_contract.mint_batch(
                company_address=company.wallet_address,
                batch_id=batch.id,
                events_count=batch.events_count
            )

            return True, result

        except Exception as e:
            self.logger.error(
                "Erro no mint blockchain",
                batch_id=batch.id,
                error=str(e)
            )
            return False, {"error": str(e)}

    async def _simulate_blockchain_mint(self, batch: TokenBatch) -> tuple[bool, Dict[str, Any]]:
        """Simula mint na blockchain (fallback)."""
        # Simular delay de rede
        await asyncio.sleep(2)

        # Simular sucesso/falha (90% de sucesso)
        import random
        import hashlib

        success = random.random() > 0.1

        if success:
            # Simular dados de transação
            tx_data = f"{batch.id}{batch.company_id}{datetime.utcnow().timestamp()}"
            tx_hash = "0x" + hashlib.sha256(tx_data.encode()).hexdigest()[:40]

            return True, {
                "tx_hash": tx_hash,
                "block_number": random.randint(40000000, 50000000),
                "gas_used": random.randint(50000, 100000),
                "status": "success"
            }
        else:
            return False, {"error": "Simulação de falha na blockchain"}
    
    async def _update_company_tokens(self, batch: TokenBatch) -> None:
        """Atualiza contadores de tokens da empresa."""
        company = await self.storage.get_company(batch.company_id)
        if company:
            company.total_tokens_earned += batch.company_tokens
            await self.storage.save_company(company)
    
    # Métodos públicos para gerenciamento
    
    async def create_company(
        self,
        company_id: str,
        name: str,
        wallet_address: Optional[str] = None,
        events_per_token: int = 1000,
        register_on_blockchain: bool = True
    ) -> Company:
        """Cria uma nova empresa e opcionalmente registra na blockchain."""
        company = Company(
            id=company_id,
            name=name,
            wallet_address=wallet_address,
            api_key=f"prfi_{company_id}",
            secret_key=f"secret_{company_id}_{datetime.utcnow().timestamp()}",
            events_per_token=events_per_token
        )

        # Salvar no banco local
        await self.storage.save_company(company)

        # Registrar na blockchain se habilitado e wallet fornecida
        if (register_on_blockchain and
            self.blockchain_enabled and
            self.prfic_contract and
            wallet_address):

            try:
                result = await self.prfic_contract.register_company(
                    company_address=wallet_address,
                    company_name=name
                )

                self.logger.info(
                    "Empresa registrada na blockchain",
                    company_id=company_id,
                    name=name,
                    wallet_address=wallet_address,
                    tx_hash=result.get("tx_hash")
                )

            except Exception as e:
                self.logger.warning(
                    "Falha ao registrar empresa na blockchain",
                    company_id=company_id,
                    error=str(e)
                )

        self.logger.info(
            "Nova empresa criada",
            company_id=company_id,
            name=name,
            wallet_address=wallet_address,
            blockchain_registered=register_on_blockchain and wallet_address is not None
        )

        return company
    
    async def get_company(self, company_id: str) -> Optional[Company]:
        """Busca empresa por ID."""
        return await self.storage.get_company(company_id)
    
    async def list_companies(self, limit: int = 100, offset: int = 0) -> List[Company]:
        """Lista empresas."""
        return await self.storage.list_companies(limit, offset)
    
    async def get_company_metrics(self, company_id: str) -> Dict[str, Any]:
        """Obtém métricas de uma empresa."""
        return await self.event_counter.get_company_metrics(company_id)
    
    async def get_company_batches(
        self,
        company_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[TokenBatch]:
        """Busca lotes de uma empresa."""
        return await self.storage.get_company_batches(company_id, limit, offset)
    
    async def retry_failed_batch(self, batch_id: str) -> bool:
        """Tenta reprocessar um lote falhado."""
        batch = await self.storage.get_token_batch(batch_id)
        
        if not batch:
            return False
        
        if batch.status != TokenBatchStatus.FAILED:
            return False
        
        if batch.retry_count >= self.max_retry_attempts:
            self.logger.warning(
                "Lote excedeu máximo de tentativas",
                batch_id=batch_id,
                retry_count=batch.retry_count
            )
            return False
        
        # Resetar para pending
        batch.status = TokenBatchStatus.PENDING
        batch.error_message = None
        await self.storage.update_token_batch(batch)
        
        self.logger.info(
            "Lote marcado para retry",
            batch_id=batch_id,
            retry_count=batch.retry_count + 1
        )
        
        return True
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Obtém métricas gerais do sistema."""
        try:
            # Buscar todas as empresas
            companies = await self.storage.list_companies(limit=1000)
            
            # Buscar lotes recentes
            all_batches = []
            for company in companies:
                batches = await self.storage.get_company_batches(company.id, limit=100)
                all_batches.extend(batches)
            
            # Calcular métricas
            total_events = sum(c.total_events for c in companies)
            total_tokens = sum(c.total_tokens_earned for c in companies)
            
            successful_batches = [b for b in all_batches if b.status == TokenBatchStatus.MINTED]
            failed_batches = [b for b in all_batches if b.status == TokenBatchStatus.FAILED]
            pending_batches = [b for b in all_batches if b.status == TokenBatchStatus.PENDING]
            
            return {
                "companies_count": len(companies),
                "total_events_processed": total_events,
                "total_tokens_minted": total_tokens,
                "total_batches": len(all_batches),
                "successful_batches": len(successful_batches),
                "failed_batches": len(failed_batches),
                "pending_batches": len(pending_batches),
                "success_rate": len(successful_batches) / max(1, len(all_batches)) * 100,
                "average_events_per_company": total_events / max(1, len(companies)),
                "average_tokens_per_company": total_tokens / max(1, len(companies))
            }
            
        except Exception as e:
            self.logger.error("Erro ao calcular métricas do sistema", error=str(e))
            return {"error": str(e)}

    async def get_blockchain_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas da blockchain."""
        if not self.blockchain_enabled or not self.prfic_contract:
            return {
                "blockchain_enabled": False,
                "error": "Blockchain não habilitada"
            }

        try:
            stats = await self.prfic_contract.get_global_stats()
            stats["blockchain_enabled"] = True
            return stats

        except Exception as e:
            self.logger.error("Erro ao obter estatísticas da blockchain", error=str(e))
            return {
                "blockchain_enabled": True,
                "error": str(e)
            }

    async def get_company_blockchain_stats(self, company_id: str) -> Dict[str, Any]:
        """Obtém estatísticas de uma empresa na blockchain."""
        if not self.blockchain_enabled or not self.prfic_contract:
            return {
                "blockchain_enabled": False,
                "error": "Blockchain não habilitada"
            }

        try:
            company = await self.storage.get_company(company_id)
            if not company or not company.wallet_address:
                return {"error": "Empresa não encontrada ou sem wallet"}

            stats = await self.prfic_contract.get_company_stats(company.wallet_address)
            stats["blockchain_enabled"] = True
            stats["company_id"] = company_id
            stats["company_name"] = company.name

            return stats

        except Exception as e:
            self.logger.error(
                "Erro ao obter estatísticas da empresa na blockchain",
                company_id=company_id,
                error=str(e)
            )
            return {
                "blockchain_enabled": True,
                "company_id": company_id,
                "error": str(e)
            }

    async def get_token_balance(self, wallet_address: str) -> Dict[str, Any]:
        """Obtém saldo de tokens de uma wallet."""
        if not self.blockchain_enabled or not self.prfic_contract:
            return {
                "blockchain_enabled": False,
                "balance": 0.0,
                "error": "Blockchain não habilitada"
            }

        try:
            balance = await self.prfic_contract.get_balance(wallet_address)

            return {
                "blockchain_enabled": True,
                "wallet_address": wallet_address,
                "balance": balance,
                "currency": "PRFIC"
            }

        except Exception as e:
            self.logger.error(
                "Erro ao obter saldo da wallet",
                wallet_address=wallet_address,
                error=str(e)
            )
            return {
                "blockchain_enabled": True,
                "wallet_address": wallet_address,
                "balance": 0.0,
                "error": str(e)
            }
