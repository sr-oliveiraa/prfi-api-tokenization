"""
Scanner de blocos pendentes para submissão.

Responsável por:
- Escanear diretório de blocos pendentes
- Filtrar blocos válidos para submissão
- Ordenar por prioridade (timestamp, pontos)
- Detectar blocos órfãos ou corrompidos
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any

import structlog

from minerador.models import MiningBlock, BlockStatus
from minerador.storage import LocalBlockStorage
from .models import SubmissionConfig

logger = structlog.get_logger(__name__)


class BlockScanner:
    """Scanner de blocos pendentes para submissão."""
    
    def __init__(self, config: SubmissionConfig):
        """
        Inicializa o scanner.
        
        Args:
            config: Configuração do sistema de submissão
        """
        self.config = config
        self.storage = LocalBlockStorage(config.blocks_directory)
        self.logger = logger.bind(component="block_scanner")
        
        # Cache de blocos escaneados
        self._last_scan: Optional[datetime] = None
        self._cached_blocks: List[MiningBlock] = []
        self._cache_ttl = timedelta(seconds=30)  # Cache válido por 30 segundos
    
    def scan_pending_blocks(self, force_refresh: bool = False) -> List[MiningBlock]:
        """
        Escaneia blocos pendentes de submissão.
        
        Args:
            force_refresh: Forçar refresh do cache
            
        Returns:
            Lista de blocos pendentes ordenados por prioridade
        """
        try:
            # Verificar cache
            if not force_refresh and self._is_cache_valid():
                self.logger.debug("Usando cache de blocos pendentes")
                return self._cached_blocks.copy()
            
            self.logger.info("Escaneando blocos pendentes")
            
            # Obter blocos pendentes do storage
            pending_blocks = self.storage.get_blocks_by_status(BlockStatus.PENDING)
            
            # Filtrar blocos válidos
            valid_blocks = []
            for block in pending_blocks:
                if self._is_block_valid_for_submission(block):
                    valid_blocks.append(block)
                else:
                    self.logger.warning(
                        "Bloco inválido encontrado",
                        block_id=block.block_id,
                        event_id=block.event_id
                    )
            
            # Ordenar por prioridade
            sorted_blocks = self._sort_blocks_by_priority(valid_blocks)
            
            # Atualizar cache
            self._cached_blocks = sorted_blocks
            self._last_scan = datetime.utcnow()
            
            self.logger.info(
                "Scan concluído",
                total_pending=len(pending_blocks),
                valid_blocks=len(valid_blocks),
                sorted_blocks=len(sorted_blocks)
            )
            
            return sorted_blocks.copy()
            
        except Exception as e:
            self.logger.error(
                "Erro no scan de blocos pendentes",
                error=str(e)
            )
            return []
    
    def get_blocks_for_batch(self, max_blocks: int) -> List[MiningBlock]:
        """
        Obtém blocos para formar um batch de submissão.
        
        Args:
            max_blocks: Número máximo de blocos
            
        Returns:
            Lista de blocos para o batch
        """
        pending_blocks = self.scan_pending_blocks()
        
        # Limitar ao número máximo
        batch_blocks = pending_blocks[:max_blocks]
        
        self.logger.info(
            "Blocos selecionados para batch",
            requested=max_blocks,
            available=len(pending_blocks),
            selected=len(batch_blocks)
        )
        
        return batch_blocks
    
    def get_blocks_by_miner(self, miner: str, limit: int = 100) -> List[MiningBlock]:
        """
        Obtém blocos pendentes de um minerador específico.
        
        Args:
            miner: Endereço do minerador
            limit: Limite de blocos
            
        Returns:
            Lista de blocos do minerador
        """
        all_blocks = self.scan_pending_blocks()
        
        miner_blocks = [
            block for block in all_blocks
            if block.miner == miner
        ]
        
        return miner_blocks[:limit]
    
    def get_oldest_blocks(self, count: int) -> List[MiningBlock]:
        """
        Obtém os blocos mais antigos pendentes.
        
        Args:
            count: Número de blocos
            
        Returns:
            Lista dos blocos mais antigos
        """
        all_blocks = self.scan_pending_blocks()
        
        # Ordenar por timestamp (mais antigo primeiro)
        oldest_blocks = sorted(all_blocks, key=lambda b: b.timestamp)
        
        return oldest_blocks[:count]
    
    def get_high_value_blocks(self, min_points: float, count: int) -> List[MiningBlock]:
        """
        Obtém blocos com alta pontuação.
        
        Args:
            min_points: Pontuação mínima
            count: Número máximo de blocos
            
        Returns:
            Lista de blocos de alto valor
        """
        all_blocks = self.scan_pending_blocks()
        
        # Filtrar por pontuação mínima
        high_value_blocks = [
            block for block in all_blocks
            if block.points >= min_points
        ]
        
        # Ordenar por pontuação (maior primeiro)
        high_value_blocks.sort(key=lambda b: b.points, reverse=True)
        
        return high_value_blocks[:count]
    
    def _is_cache_valid(self) -> bool:
        """Verifica se o cache ainda é válido."""
        if self._last_scan is None:
            return False
        
        return datetime.utcnow() - self._last_scan < self._cache_ttl
    
    def _is_block_valid_for_submission(self, block: MiningBlock) -> bool:
        """
        Verifica se um bloco é válido para submissão.
        
        Args:
            block: Bloco a ser validado
            
        Returns:
            True se o bloco é válido
        """
        try:
            # Verificar campos obrigatórios
            if not all([
                block.block_id,
                block.event_id,
                block.signature,
                block.public_key,
                block.miner
            ]):
                return False
            
            # Verificar status
            if block.status != 200:
                return False
            
            # Verificar pontos
            if block.points <= 0:
                return False
            
            # Verificar timestamp (não muito antigo nem futuro)
            now = datetime.utcnow()
            if block.timestamp > now + timedelta(minutes=5):
                return False
            
            if block.timestamp < now - timedelta(days=7):
                return False
            
            # Verificar se não foi já submetido
            if block.block_status != BlockStatus.PENDING:
                return False
            
            return True
            
        except Exception as e:
            self.logger.warning(
                "Erro na validação de bloco",
                block_id=block.block_id,
                error=str(e)
            )
            return False
    
    def _sort_blocks_by_priority(self, blocks: List[MiningBlock]) -> List[MiningBlock]:
        """
        Ordena blocos por prioridade de submissão.

        Critérios de prioridade:
        1. Blocos mais antigos primeiro (FIFO)
        2. Blocos com mais pontos primeiro (dentro do mesmo período)
        3. Mineradores com menos blocos submetidos recentemente

        Args:
            blocks: Lista de blocos para ordenar

        Returns:
            Lista ordenada por prioridade
        """
        def priority_key(block: MiningBlock) -> tuple:
            # Timestamp como prioridade principal (mais antigo = menor valor)
            timestamp_priority = block.timestamp.timestamp()

            # Pontos como prioridade secundária (mais pontos = menor valor)
            points_priority = -block.points

            # ID do bloco como desempate
            block_id_priority = block.block_id

            return (timestamp_priority, points_priority, block_id_priority)

        return sorted(blocks, key=priority_key)
    
    def get_scan_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do scanner."""
        pending_blocks = self.scan_pending_blocks()
        
        if not pending_blocks:
            return {
                "total_pending": 0,
                "oldest_block": None,
                "newest_block": None,
                "total_points": 0.0,
                "unique_miners": 0,
                "last_scan": self._last_scan.isoformat() if self._last_scan else None
            }
        
        # Calcular estatísticas
        timestamps = [block.timestamp for block in pending_blocks]
        points = [block.points for block in pending_blocks]
        miners = set(block.miner for block in pending_blocks)
        
        return {
            "total_pending": len(pending_blocks),
            "oldest_block": min(timestamps).isoformat(),
            "newest_block": max(timestamps).isoformat(),
            "total_points": sum(points),
            "avg_points": sum(points) / len(points),
            "unique_miners": len(miners),
            "last_scan": self._last_scan.isoformat() if self._last_scan else None,
            "cache_valid": self._is_cache_valid()
        }
    
    def clear_cache(self) -> None:
        """Limpa o cache de blocos."""
        self._cached_blocks = []
        self._last_scan = None
        self.logger.debug("Cache de blocos limpo")
    
    def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do scanner."""
        try:
            # Tentar escanear blocos
            blocks = self.scan_pending_blocks()
            
            # Verificar se diretório existe
            blocks_dir = Path(self.config.blocks_directory)
            dir_exists = blocks_dir.exists()
            
            # Verificar permissões
            can_read = os.access(blocks_dir, os.R_OK) if dir_exists else False
            
            return {
                "healthy": True,
                "blocks_directory_exists": dir_exists,
                "can_read_directory": can_read,
                "pending_blocks_found": len(blocks),
                "last_scan": self._last_scan.isoformat() if self._last_scan else None,
                "cache_status": "valid" if self._is_cache_valid() else "invalid"
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "blocks_directory_exists": False,
                "can_read_directory": False,
                "pending_blocks_found": 0
            }
