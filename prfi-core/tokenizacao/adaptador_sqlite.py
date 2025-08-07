"""
Adaptador SQLite específico para tokenização PRFIC.

Estende o adaptador SQLite base com funcionalidades de tokenização.
"""

import json
from datetime import datetime
from typing import List, Optional
from uuid import UUID

import structlog

from ..armazenamento.adaptador_sqlite import SQLiteAdapter
from ..excecoes import StorageException
from .contador import EventCounter
from .modelos import Company, TokenBatch, EventLedger, TokenizationMetrics


logger = structlog.get_logger(__name__)


class TokenizationSQLiteAdapter(SQLiteAdapter):
    """Adaptador SQLite com suporte a tokenização."""
    
    def __init__(self, config):
        super().__init__(config)
        self.logger = logger.bind(component="tokenization_sqlite")
    
    # Métodos para Companies
    async def get_company(self, company_id: str) -> Optional[Company]:
        """Busca empresa por ID."""
        try:
            conn = await self._get_connection()
            cursor = await conn.execute(
                "SELECT * FROM companies WHERE id = ?",
                (company_id,)
            )
            row = await cursor.fetchone()
            
            if row:
                # Converter Row para dict manualmente
                row_dict = {
                    "id": row[0],
                    "name": row[1],
                    "wallet_address": row[2],
                    "api_key": row[3],
                    "secret_key": row[4],
                    "events_per_token": row[5],
                    "auto_mint": row[6],
                    "total_events": row[7],
                    "current_batch_events": row[8],
                    "total_tokens_earned": row[9],
                    "created_at": row[10],
                    "updated_at": row[11]
                }
                return self._row_to_company(row_dict)
            return None
            
        except Exception as e:
            raise StorageException(
                message=f"Erro ao buscar empresa: {str(e)}",
                storage_type="sqlite",
                operation="get_company"
            )
    
    async def save_company(self, company: Company) -> None:
        """Salva ou atualiza empresa."""
        try:
            conn = await self._get_connection()
            
            # Verificar se empresa existe
            existing = await self.get_company(company.id)
            
            if existing:
                # Atualizar
                await conn.execute("""
                    UPDATE companies SET
                        name = ?, wallet_address = ?, api_key = ?, secret_key = ?,
                        events_per_token = ?, auto_mint = ?, total_events = ?,
                        current_batch_events = ?, total_tokens_earned = ?, updated_at = ?
                    WHERE id = ?
                """, (
                    company.name, company.wallet_address, company.api_key, company.secret_key,
                    company.events_per_token, int(company.auto_mint), company.total_events,
                    company.current_batch_events, company.total_tokens_earned,
                    datetime.utcnow().isoformat(), company.id
                ))
            else:
                # Inserir
                await conn.execute("""
                    INSERT INTO companies (
                        id, name, wallet_address, api_key, secret_key,
                        events_per_token, auto_mint, total_events,
                        current_batch_events, total_tokens_earned, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    company.id, company.name, company.wallet_address, company.api_key, company.secret_key,
                    company.events_per_token, int(company.auto_mint), company.total_events,
                    company.current_batch_events, company.total_tokens_earned,
                    company.created_at.isoformat(), company.updated_at.isoformat()
                ))
            
            await conn.commit()
            
        except Exception as e:
            raise StorageException(
                message=f"Erro ao salvar empresa: {str(e)}",
                storage_type="sqlite",
                operation="save_company"
            )
    
    async def list_companies(self, limit: int = 100, offset: int = 0) -> List[Company]:
        """Lista empresas com paginação."""
        try:
            conn = await self._get_connection()
            cursor = await conn.execute(
                "SELECT * FROM companies ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset)
            )
            rows = await cursor.fetchall()
            
            companies = []
            for row in rows:
                # Converter Row para dict manualmente
                row_dict = {
                    "id": row[0],
                    "name": row[1],
                    "wallet_address": row[2],
                    "api_key": row[3],
                    "secret_key": row[4],
                    "events_per_token": row[5],
                    "auto_mint": row[6],
                    "total_events": row[7],
                    "current_batch_events": row[8],
                    "total_tokens_earned": row[9],
                    "created_at": row[10],
                    "updated_at": row[11]
                }
                companies.append(self._row_to_company(row_dict))
            return companies
            
        except Exception as e:
            raise StorageException(
                message=f"Erro ao listar empresas: {str(e)}",
                storage_type="sqlite",
                operation="list_companies"
            )
    
    # Métodos para Token Batches
    async def save_token_batch(self, batch: TokenBatch) -> None:
        """Salva lote de tokens."""
        try:
            conn = await self._get_connection()
            
            await conn.execute("""
                INSERT INTO token_batches (
                    id, company_id, events_count, batch_hash, tokens_to_mint,
                    company_tokens, developer_tokens, blockchain_tx_hash, block_number,
                    gas_used, status, error_message, retry_count, created_at,
                    processed_at, minted_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                batch.id, batch.company_id, batch.events_count, batch.batch_hash,
                batch.tokens_to_mint, batch.company_tokens, batch.developer_tokens,
                batch.blockchain_tx_hash, batch.block_number, batch.gas_used,
                batch.status.value, batch.error_message, batch.retry_count,
                batch.created_at.isoformat(),
                batch.processed_at.isoformat() if batch.processed_at else None,
                batch.minted_at.isoformat() if batch.minted_at else None
            ))
            
            await conn.commit()
            
        except Exception as e:
            raise StorageException(
                message=f"Erro ao salvar token batch: {str(e)}",
                storage_type="sqlite",
                operation="save_token_batch"
            )
    
    async def get_token_batch(self, batch_id: str) -> Optional[TokenBatch]:
        """Busca lote de tokens por ID."""
        try:
            conn = await self._get_connection()
            cursor = await conn.execute(
                "SELECT * FROM token_batches WHERE id = ?",
                (batch_id,)
            )
            row = await cursor.fetchone()
            
            if row:
                # Converter Row para dict manualmente
                row_dict = {
                    "id": row[0],
                    "company_id": row[1],
                    "events_count": row[2],
                    "batch_hash": row[3],
                    "tokens_to_mint": row[4],
                    "company_tokens": row[5],
                    "developer_tokens": row[6],
                    "blockchain_tx_hash": row[7],
                    "block_number": row[8],
                    "gas_used": row[9],
                    "status": row[10],
                    "error_message": row[11],
                    "retry_count": row[12],
                    "created_at": row[13],
                    "processed_at": row[14],
                    "minted_at": row[15]
                }
                return self._row_to_token_batch(row_dict)
            return None
            
        except Exception as e:
            raise StorageException(
                message=f"Erro ao buscar token batch: {str(e)}",
                storage_type="sqlite",
                operation="get_token_batch"
            )
    
    async def update_token_batch(self, batch: TokenBatch) -> None:
        """Atualiza lote de tokens."""
        try:
            conn = await self._get_connection()
            
            await conn.execute("""
                UPDATE token_batches SET
                    blockchain_tx_hash = ?, block_number = ?, gas_used = ?,
                    status = ?, error_message = ?, retry_count = ?,
                    processed_at = ?, minted_at = ?
                WHERE id = ?
            """, (
                batch.blockchain_tx_hash, batch.block_number, batch.gas_used,
                batch.status.value, batch.error_message, batch.retry_count,
                batch.processed_at.isoformat() if batch.processed_at else None,
                batch.minted_at.isoformat() if batch.minted_at else None,
                batch.id
            ))
            
            await conn.commit()
            
        except Exception as e:
            raise StorageException(
                message=f"Erro ao atualizar token batch: {str(e)}",
                storage_type="sqlite",
                operation="update_token_batch"
            )
    
    async def get_company_batches(
        self, 
        company_id: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[TokenBatch]:
        """Busca lotes de uma empresa."""
        try:
            conn = await self._get_connection()
            cursor = await conn.execute("""
                SELECT * FROM token_batches 
                WHERE company_id = ? 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """, (company_id, limit, offset))
            rows = await cursor.fetchall()
            
            batches = []
            for row in rows:
                # Converter Row para dict manualmente
                row_dict = {
                    "id": row[0],
                    "company_id": row[1],
                    "events_count": row[2],
                    "batch_hash": row[3],
                    "tokens_to_mint": row[4],
                    "company_tokens": row[5],
                    "developer_tokens": row[6],
                    "blockchain_tx_hash": row[7],
                    "block_number": row[8],
                    "gas_used": row[9],
                    "status": row[10],
                    "error_message": row[11],
                    "retry_count": row[12],
                    "created_at": row[13],
                    "processed_at": row[14],
                    "minted_at": row[15]
                }
                batches.append(self._row_to_token_batch(row_dict))
            return batches
            
        except Exception as e:
            raise StorageException(
                message=f"Erro ao buscar lotes da empresa: {str(e)}",
                storage_type="sqlite",
                operation="get_company_batches"
            )
    
    async def get_pending_batches(self, limit: int = 10) -> List[TokenBatch]:
        """Busca lotes pendentes para processamento."""
        try:
            conn = await self._get_connection()
            cursor = await conn.execute("""
                SELECT * FROM token_batches 
                WHERE status IN ('pending', 'processing') 
                ORDER BY created_at ASC 
                LIMIT ?
            """, (limit,))
            rows = await cursor.fetchall()
            
            batches = []
            for row in rows:
                # Converter Row para dict manualmente
                row_dict = {
                    "id": row[0],
                    "company_id": row[1],
                    "events_count": row[2],
                    "batch_hash": row[3],
                    "tokens_to_mint": row[4],
                    "company_tokens": row[5],
                    "developer_tokens": row[6],
                    "blockchain_tx_hash": row[7],
                    "block_number": row[8],
                    "gas_used": row[9],
                    "status": row[10],
                    "error_message": row[11],
                    "retry_count": row[12],
                    "created_at": row[13],
                    "processed_at": row[14],
                    "minted_at": row[15]
                }
                batches.append(self._row_to_token_batch(row_dict))
            return batches
            
        except Exception as e:
            raise StorageException(
                message=f"Erro ao buscar lotes pendentes: {str(e)}",
                storage_type="sqlite",
                operation="get_pending_batches"
            )
    
    # Métodos para Event Ledger
    async def save_ledger_entry(self, entry: EventLedger) -> None:
        """Salva entrada no ledger."""
        try:
            conn = await self._get_connection()
            
            await conn.execute("""
                INSERT INTO event_ledger (
                    id, event_id, company_id, batch_id, ip_address, user_agent,
                    event_type, url, payload_hash, signature, processed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.id, entry.event_id, entry.company_id, entry.batch_id,
                entry.ip_address, entry.user_agent, entry.event_type, entry.url,
                entry.payload_hash, entry.signature, entry.processed_at.isoformat()
            ))
            
            await conn.commit()
            
        except Exception as e:
            raise StorageException(
                message=f"Erro ao salvar ledger entry: {str(e)}",
                storage_type="sqlite",
                operation="save_ledger_entry"
            )
    
    # Métodos de conversão
    def _row_to_company(self, row: dict) -> Company:
        """Converte linha do banco para Company."""
        return Company(
            id=row["id"],
            name=row["name"],
            wallet_address=row["wallet_address"],
            api_key=row["api_key"],
            secret_key=row["secret_key"],
            events_per_token=row["events_per_token"],
            auto_mint=bool(row["auto_mint"]),
            total_events=row["total_events"],
            current_batch_events=row["current_batch_events"],
            total_tokens_earned=row["total_tokens_earned"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"])
        )
    
    def _row_to_token_batch(self, row: dict) -> TokenBatch:
        """Converte linha do banco para TokenBatch."""
        from .modelos import TokenBatchStatus
        
        return TokenBatch(
            id=row["id"],
            company_id=row["company_id"],
            events_count=row["events_count"],
            batch_hash=row["batch_hash"],
            tokens_to_mint=row["tokens_to_mint"],
            company_tokens=row["company_tokens"],
            developer_tokens=row["developer_tokens"],
            blockchain_tx_hash=row["blockchain_tx_hash"],
            block_number=row["block_number"],
            gas_used=row["gas_used"],
            status=TokenBatchStatus(row["status"]),
            error_message=row["error_message"],
            retry_count=row["retry_count"],
            created_at=datetime.fromisoformat(row["created_at"]),
            processed_at=datetime.fromisoformat(row["processed_at"]) if row["processed_at"] else None,
            minted_at=datetime.fromisoformat(row["minted_at"]) if row["minted_at"] else None
        )
