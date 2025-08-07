"""
Sistema de batching para otimizar submissões blockchain.

Responsável por:
- Agrupar blocos em batches otimizados
- Balancear tamanho vs custo de gas
- Priorizar blocos por idade e valor
- Otimizar distribuição entre mineradores
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import uuid4

import structlog

from minerador.models import MiningBlock
from .models import SubmissionConfig, SubmissionBatch, BatchStatus

logger = structlog.get_logger(__name__)


class BlockBatcher:
    """Sistema de batching para blocos de submissão."""
    
    def __init__(self, config: SubmissionConfig):
        """
        Inicializa o batcher.
        
        Args:
            config: Configuração do sistema de submissão
        """
        self.config = config
        self.logger = logger.bind(component="block_batcher")
    
    def create_batches(self, blocks: List[MiningBlock]) -> List[SubmissionBatch]:
        """
        Cria batches otimizados a partir de uma lista de blocos.
        
        Args:
            blocks: Lista de blocos para agrupar
            
        Returns:
            Lista de batches criados
        """
        if not blocks:
            return []
        
        self.logger.info(
            "Criando batches",
            total_blocks=len(blocks),
            target_batch_size=self.config.batch_size
        )
        
        # Ordenar blocos por prioridade
        sorted_blocks = self._sort_blocks_for_batching(blocks)
        
        # Criar batches
        batches = []
        current_batch_blocks = []
        
        for block in sorted_blocks:
            current_batch_blocks.append(block)
            
            # Verificar se deve criar um novo batch
            if self._should_create_batch(current_batch_blocks):
                batch = self._create_batch_from_blocks(current_batch_blocks)
                batches.append(batch)
                current_batch_blocks = []
        
        # Criar batch final se houver blocos restantes
        if current_batch_blocks:
            batch = self._create_batch_from_blocks(current_batch_blocks)
            batches.append(batch)
        
        self.logger.info(
            "Batches criados",
            total_batches=len(batches),
            total_blocks=sum(len(batch.blocks) for batch in batches)
        )
        
        return batches
    
    def create_single_batch(self, blocks: List[MiningBlock]) -> Optional[SubmissionBatch]:
        """
        Cria um único batch a partir de blocos.
        
        Args:
            blocks: Lista de blocos
            
        Returns:
            Batch criado ou None se não há blocos
        """
        if not blocks:
            return None
        
        return self._create_batch_from_blocks(blocks)
    
    def optimize_batch_size(self, blocks: List[MiningBlock], target_gas: int) -> List[MiningBlock]:
        """
        Otimiza o tamanho do batch baseado no gas target.
        
        Args:
            blocks: Lista de blocos candidatos
            target_gas: Gas target para o batch
            
        Returns:
            Lista otimizada de blocos
        """
        if not blocks:
            return []
        
        # Estimar gas por bloco (aproximadamente)
        gas_per_block = 21000  # Estimativa base
        max_blocks = min(target_gas // gas_per_block, len(blocks))
        
        # Selecionar os melhores blocos dentro do limite
        optimized_blocks = self._select_best_blocks(blocks, max_blocks)
        
        self.logger.debug(
            "Batch otimizado por gas",
            original_blocks=len(blocks),
            optimized_blocks=len(optimized_blocks),
            target_gas=target_gas,
            estimated_gas=len(optimized_blocks) * gas_per_block
        )
        
        return optimized_blocks
    
    def balance_miners(self, blocks: List[MiningBlock]) -> List[MiningBlock]:
        """
        Balanceia blocos entre diferentes mineradores.
        
        Args:
            blocks: Lista de blocos
            
        Returns:
            Lista balanceada de blocos
        """
        if not blocks:
            return []
        
        # Agrupar por minerador
        miner_blocks: Dict[str, List[MiningBlock]] = {}
        for block in blocks:
            if block.miner not in miner_blocks:
                miner_blocks[block.miner] = []
            miner_blocks[block.miner].append(block)
        
        # Balancear seleção
        balanced_blocks = []
        max_per_miner = max(1, self.config.batch_size // len(miner_blocks))
        
        for miner, miner_block_list in miner_blocks.items():
            # Ordenar blocos do minerador por prioridade
            sorted_miner_blocks = sorted(
                miner_block_list,
                key=lambda b: (b.timestamp, -b.points)
            )
            
            # Selecionar até o máximo por minerador
            selected = sorted_miner_blocks[:max_per_miner]
            balanced_blocks.extend(selected)
        
        self.logger.debug(
            "Blocos balanceados entre mineradores",
            total_miners=len(miner_blocks),
            max_per_miner=max_per_miner,
            balanced_blocks=len(balanced_blocks)
        )
        
        return balanced_blocks
    
    def _sort_blocks_for_batching(self, blocks: List[MiningBlock]) -> List[MiningBlock]:
        """Ordena blocos para otimizar batching."""
        def batching_key(block: MiningBlock) -> tuple:
            # Prioridade por timestamp (mais antigo primeiro)
            timestamp_priority = block.timestamp.timestamp()
            
            # Prioridade por pontos (mais pontos primeiro)
            points_priority = -block.points
            
            # Prioridade por minerador (para balanceamento)
            miner_priority = hash(block.miner) % 1000
            
            return (timestamp_priority, points_priority, miner_priority)
        
        return sorted(blocks, key=batching_key)
    
    def _should_create_batch(self, current_blocks: List[MiningBlock]) -> bool:
        """Determina se deve criar um batch com os blocos atuais."""
        # Verificar tamanho mínimo e máximo
        if len(current_blocks) < self.config.min_batch_size:
            return False
        
        if len(current_blocks) >= self.config.max_batch_size:
            return True
        
        # Verificar tamanho target
        if len(current_blocks) >= self.config.batch_size:
            return True
        
        return False
    
    def _create_batch_from_blocks(self, blocks: List[MiningBlock]) -> SubmissionBatch:
        """Cria um batch a partir de uma lista de blocos."""
        if not blocks:
            raise ValueError("Não é possível criar batch vazio")
        
        # Calcular dados agregados
        total_points = sum(block.points for block in blocks)
        unique_miners = list(set(block.miner for block in blocks))
        block_ids = [block.block_id for block in blocks]
        
        # Criar batch
        batch = SubmissionBatch(
            blocks=blocks,
            block_ids=block_ids,
            total_points=total_points,
            miners=unique_miners,
            max_retries=self.config.max_retries
        )
        
        self.logger.debug(
            "Batch criado",
            batch_id=batch.batch_id,
            blocks_count=len(blocks),
            total_points=total_points,
            unique_miners=len(unique_miners)
        )
        
        return batch
    
    def _select_best_blocks(self, blocks: List[MiningBlock], max_count: int) -> List[MiningBlock]:
        """Seleciona os melhores blocos baseado em critérios de valor."""
        if len(blocks) <= max_count:
            return blocks
        
        # Calcular score para cada bloco
        scored_blocks = []
        for block in blocks:
            score = self._calculate_block_score(block)
            scored_blocks.append((score, block))
        
        # Ordenar por score (maior primeiro) e selecionar os melhores
        scored_blocks.sort(key=lambda x: x[0], reverse=True)
        selected_blocks = [block for _, block in scored_blocks[:max_count]]
        
        return selected_blocks
    
    def _calculate_block_score(self, block: MiningBlock) -> float:
        """Calcula score de um bloco para priorização."""
        score = 0.0
        
        # Score base pelos pontos
        score += block.points * 10
        
        # Bônus por idade (blocos mais antigos têm prioridade)
        age_hours = (datetime.utcnow() - block.timestamp).total_seconds() / 3600
        score += min(age_hours * 0.1, 2.0)  # Máximo 2 pontos por idade
        
        # Bônus por retry (indica resiliência)
        score += block.retries * 0.5
        
        # Bônus por uso de fallback
        if block.fallback_used:
            score += 1.0
        
        # Penalidade por requisições muito rápidas (possível fraude)
        if block.request_duration < 0.1:
            score -= 2.0
        
        return score
    
    def get_batch_stats(self, batches: List[SubmissionBatch]) -> Dict[str, Any]:
        """Obtém estatísticas dos batches."""
        if not batches:
            return {
                "total_batches": 0,
                "total_blocks": 0,
                "total_points": 0.0,
                "avg_batch_size": 0.0,
                "unique_miners": 0
            }
        
        total_blocks = sum(len(batch.blocks) for batch in batches)
        total_points = sum(batch.total_points for batch in batches)
        all_miners = set()
        
        for batch in batches:
            all_miners.update(batch.miners)
        
        return {
            "total_batches": len(batches),
            "total_blocks": total_blocks,
            "total_points": total_points,
            "avg_batch_size": total_blocks / len(batches),
            "unique_miners": len(all_miners),
            "min_batch_size": min(len(batch.blocks) for batch in batches),
            "max_batch_size": max(len(batch.blocks) for batch in batches)
        }
    
    def split_large_batch(self, batch: SubmissionBatch) -> List[SubmissionBatch]:
        """Divide um batch grande em batches menores."""
        if len(batch.blocks) <= self.config.max_batch_size:
            return [batch]
        
        # Dividir blocos em chunks
        blocks = batch.blocks
        chunk_size = self.config.batch_size
        
        new_batches = []
        for i in range(0, len(blocks), chunk_size):
            chunk_blocks = blocks[i:i + chunk_size]
            new_batch = self._create_batch_from_blocks(chunk_blocks)
            new_batches.append(new_batch)
        
        self.logger.info(
            "Batch dividido",
            original_batch_id=batch.batch_id,
            original_size=len(batch.blocks),
            new_batches=len(new_batches)
        )
        
        return new_batches
    
    def merge_small_batches(self, batches: List[SubmissionBatch]) -> List[SubmissionBatch]:
        """Mescla batches pequenos em batches maiores."""
        if not batches:
            return []
        
        # Separar batches pequenos e normais
        small_batches = [b for b in batches if len(b.blocks) < self.config.min_batch_size]
        normal_batches = [b for b in batches if len(b.blocks) >= self.config.min_batch_size]
        
        if not small_batches:
            return batches
        
        # Mesclar batches pequenos
        merged_blocks = []
        for batch in small_batches:
            merged_blocks.extend(batch.blocks)
        
        # Criar novos batches com os blocos mesclados
        new_batches = self.create_batches(merged_blocks)
        
        # Combinar com batches normais
        result_batches = normal_batches + new_batches
        
        self.logger.info(
            "Batches pequenos mesclados",
            original_small_batches=len(small_batches),
            new_batches=len(new_batches),
            total_result_batches=len(result_batches)
        )
        
        return result_batches
