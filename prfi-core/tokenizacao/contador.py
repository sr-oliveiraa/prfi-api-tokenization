"""
Sistema de contagem de eventos para tokenização PRFIC.

Este módulo implementa o middleware que conta eventos por empresa
e aciona a geração de tokens quando o threshold é atingido.
"""

import asyncio
import hashlib
import logging
from datetime import datetime
from typing import Optional, Dict, Any

import structlog

from ..modelos import PRFIEvent
from ..armazenamento.base import StorageAdapter
from .modelos import Company, TokenBatch, EventLedger


logger = structlog.get_logger(__name__)


class EventCounter:
    """Contador base de eventos para tokenização."""
    
    def __init__(self, storage: StorageAdapter):
        """
        Inicializa o contador de eventos.
        
        Args:
            storage: Adaptador de storage para persistência
        """
        self.storage = storage
        self.logger = logger.bind(component="event_counter")
    
    async def increment_event_count(
        self, 
        company_id: str, 
        event: PRFIEvent,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Incrementa o contador de eventos para uma empresa.
        
        Args:
            company_id: ID da empresa
            event: Evento PRFI processado
            ip_address: IP de origem (opcional)
            user_agent: User agent do cliente (opcional)
            
        Returns:
            Dict com informações do contador e se deve gerar token
        """
        try:
            # Buscar empresa
            company = await self._get_or_create_company(company_id)
            
            # Registrar no ledger de auditoria
            await self._record_event_ledger(
                company_id=company_id,
                event=event,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Incrementar contadores
            company.total_events += 1
            company.current_batch_events += 1
            company.updated_at = datetime.utcnow()
            
            # Verificar se deve gerar token
            should_mint = company.current_batch_events >= company.events_per_token
            
            result = {
                "company_id": company_id,
                "total_events": company.total_events,
                "current_batch_events": company.current_batch_events,
                "events_per_token": company.events_per_token,
                "should_mint_token": should_mint,
                "progress_percentage": (company.current_batch_events / company.events_per_token) * 100
            }
            
            if should_mint:
                # Criar lote de tokens
                batch = await self._create_token_batch(company)
                result["token_batch_id"] = batch.id
                
                # Resetar contador do lote atual
                company.current_batch_events = 0
                
                self.logger.info(
                    "Threshold atingido - token batch criado",
                    company_id=company_id,
                    batch_id=batch.id,
                    total_events=company.total_events
                )
            
            # Salvar empresa atualizada
            await self._save_company(company)
            
            self.logger.debug(
                "Evento contabilizado",
                company_id=company_id,
                event_id=str(event.prfi_event_id),
                current_batch=company.current_batch_events,
                should_mint=should_mint
            )
            
            return result
            
        except Exception as e:
            self.logger.error(
                "Erro ao incrementar contador de eventos",
                company_id=company_id,
                event_id=str(event.prfi_event_id),
                error=str(e)
            )
            raise
    
    async def get_company_metrics(self, company_id: str) -> Dict[str, Any]:
        """
        Obtém métricas de tokenização para uma empresa.
        
        Args:
            company_id: ID da empresa
            
        Returns:
            Dict com métricas da empresa
        """
        try:
            company = await self._get_company(company_id)
            if not company:
                return {"error": "Empresa não encontrada"}
            
            # Buscar lotes de tokens
            batches = await self._get_company_batches(company_id)
            
            successful_batches = [b for b in batches if b.status == "minted"]
            failed_batches = [b for b in batches if b.status == "failed"]
            
            return {
                "company_id": company_id,
                "company_name": company.name,
                "total_events": company.total_events,
                "current_batch_events": company.current_batch_events,
                "events_per_token": company.events_per_token,
                "total_tokens_earned": company.total_tokens_earned,
                "total_batches": len(batches),
                "successful_batches": len(successful_batches),
                "failed_batches": len(failed_batches),
                "success_rate": len(successful_batches) / max(1, len(batches)) * 100,
                "progress_percentage": (company.current_batch_events / company.events_per_token) * 100,
                "next_token_in": company.events_per_token - company.current_batch_events
            }
            
        except Exception as e:
            self.logger.error(
                "Erro ao obter métricas da empresa",
                company_id=company_id,
                error=str(e)
            )
            raise
    
    async def _get_or_create_company(self, company_id: str) -> Company:
        """Busca ou cria uma empresa."""
        company = await self._get_company(company_id)
        
        if not company:
            # Criar nova empresa
            company = Company(
                id=company_id,
                name=f"Empresa {company_id}",
                api_key=f"prfi_{company_id}",
                secret_key=f"secret_{company_id}"
            )
            await self._save_company(company)
            
            self.logger.info(
                "Nova empresa criada",
                company_id=company_id,
                company_name=company.name
            )
        
        return company
    
    async def _record_event_ledger(
        self,
        company_id: str,
        event: PRFIEvent,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> EventLedger:
        """Registra evento no ledger de auditoria."""
        # Gerar hash do payload para integridade
        payload_str = f"{event.prfi_event_id}{event.data}{event.prfi_timestamp}"
        payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()
        
        ledger_entry = EventLedger(
            event_id=str(event.prfi_event_id),
            company_id=company_id,
            ip_address=ip_address,
            user_agent=user_agent,
            event_type=event.event_type,
            url=event.url,
            payload_hash=payload_hash,
            signature=event.prfi_signature
        )
        
        await self._save_ledger_entry(ledger_entry)
        return ledger_entry
    
    async def _create_token_batch(self, company: Company) -> TokenBatch:
        """Cria um novo lote de tokens para mint."""
        # Gerar hash do lote para auditoria
        batch_data = f"{company.id}{company.total_events}{datetime.utcnow().isoformat()}"
        batch_hash = hashlib.sha256(batch_data.encode()).hexdigest()
        
        batch = TokenBatch(
            company_id=company.id,
            events_count=company.events_per_token,
            batch_hash=batch_hash,
            tokens_to_mint=1.0,
            company_tokens=0.8,
            developer_tokens=0.2
        )
        
        await self._save_token_batch(batch)
        return batch
    
    # Métodos abstratos que devem ser implementados pelos adaptadores
    async def _get_company(self, company_id: str) -> Optional[Company]:
        """Busca empresa por ID."""
        raise NotImplementedError
    
    async def _save_company(self, company: Company) -> None:
        """Salva empresa."""
        raise NotImplementedError
    
    async def _save_ledger_entry(self, entry: EventLedger) -> None:
        """Salva entrada no ledger."""
        raise NotImplementedError
    
    async def _save_token_batch(self, batch: TokenBatch) -> None:
        """Salva lote de tokens."""
        raise NotImplementedError
    
    async def _get_company_batches(self, company_id: str) -> list:
        """Busca lotes de uma empresa."""
        raise NotImplementedError


class CompanyEventCounter(EventCounter):
    """Implementação específica do contador para empresas."""

    def __init__(self, tokenization_storage):
        """
        Inicializa contador com storage de tokenização.

        Args:
            tokenization_storage: Adaptador de storage com suporte a tokenização
        """
        # Usar o storage base do adaptador de tokenização
        super().__init__(tokenization_storage)
        self.tokenization_storage = tokenization_storage
        self._companies_cache: Dict[str, Company] = {}
        self._cache_ttl = 300  # 5 minutos
        self._last_cache_update: Dict[str, datetime] = {}

    async def _get_company(self, company_id: str) -> Optional[Company]:
        """Busca empresa com cache."""
        # Verificar cache
        if company_id in self._companies_cache:
            last_update = self._last_cache_update.get(company_id)
            if last_update and (datetime.utcnow() - last_update).seconds < self._cache_ttl:
                return self._companies_cache[company_id]

        # Buscar no storage
        company = await self.tokenization_storage.get_company(company_id)

        # Atualizar cache se encontrou
        if company:
            self._companies_cache[company_id] = company
            self._last_cache_update[company_id] = datetime.utcnow()

        return company

    async def _save_company(self, company: Company) -> None:
        """Salva empresa e atualiza cache."""
        # Salvar no storage
        await self.tokenization_storage.save_company(company)

        # Atualizar cache
        self._companies_cache[company.id] = company
        self._last_cache_update[company.id] = datetime.utcnow()

        self.logger.debug("Empresa salva", company_id=company.id)

    async def _save_ledger_entry(self, entry: EventLedger) -> None:
        """Salva entrada no ledger."""
        await self.tokenization_storage.save_ledger_entry(entry)
        self.logger.debug("Ledger entry salva", entry_id=entry.id)

    async def _save_token_batch(self, batch: TokenBatch) -> None:
        """Salva lote de tokens."""
        await self.tokenization_storage.save_token_batch(batch)
        self.logger.debug("Token batch salvo", batch_id=batch.id)

    async def _get_company_batches(self, company_id: str) -> list:
        """Busca lotes de uma empresa."""
        return await self.tokenization_storage.get_company_batches(company_id)
