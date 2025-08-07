"""
Validador de eventos para submissão blockchain
"""

from typing import List, Tuple, Dict, Any
from minerador.models import MiningBlock


class EventValidator:
    """Validador de eventos para submissão"""
    
    def __init__(self, config=None):
        """
        Inicializa o validador
        
        Args:
            config: Configuração do validador
        """
        self.config = config or {}
        self.validation_stats = {
            'total_validated': 0,
            'valid_blocks': 0,
            'invalid_blocks': 0,
            'errors': []
        }
    
    def validate_blocks(self, blocks: List[MiningBlock]) -> Tuple[List[MiningBlock], List[str]]:
        """
        Valida uma lista de blocos
        
        Args:
            blocks: Lista de blocos para validar
            
        Returns:
            Tuple com (blocos_válidos, erros)
        """
        valid_blocks = []
        errors = []
        
        for block in blocks:
            is_valid, block_errors = self.validate_block(block)
            
            if is_valid:
                valid_blocks.append(block)
                self.validation_stats['valid_blocks'] += 1
            else:
                errors.extend(block_errors)
                self.validation_stats['invalid_blocks'] += 1
            
            self.validation_stats['total_validated'] += 1
        
        return valid_blocks, errors
    
    def validate_block(self, block: MiningBlock) -> Tuple[bool, List[str]]:
        """
        Valida um bloco individual
        
        Args:
            block: Bloco para validar
            
        Returns:
            Tuple com (is_valid, errors)
        """
        errors = []
        
        # Validar campos obrigatórios
        if not block.block_id:
            errors.append("Block ID é obrigatório")
        
        if not block.event_id:
            errors.append("Event ID é obrigatório")
        
        if not block.miner:
            errors.append("Miner address é obrigatório")
        
        if not block.signature:
            errors.append("Signature é obrigatória")
        
        if not block.payload_hash:
            errors.append("Payload hash é obrigatório")
        
        # Validar valores
        if block.points <= 0:
            errors.append("Points deve ser maior que zero")
        
        if block.status != 200:
            errors.append(f"Status deve ser 200, recebido: {block.status}")
        
        # Validar assinatura (implementação básica)
        if not self._validate_signature(block):
            errors.append("Assinatura inválida")
        
        return len(errors) == 0, errors
    
    def _validate_signature(self, block: MiningBlock) -> bool:
        """
        Valida a assinatura de um bloco
        
        Args:
            block: Bloco para validar
            
        Returns:
            True se assinatura é válida
        """
        # Implementação básica - em produção usar verificação criptográfica real
        signing_data = block.get_signing_data()
        expected_signature = f"signature_{hash(signing_data) % 1000000}"
        
        return block.signature.endswith(str(hash(signing_data) % 1000)[:6])
    
    def prepare_for_submission(self, blocks: List[MiningBlock]) -> Dict[str, Any]:
        """
        Prepara blocos para submissão no contrato
        
        Args:
            blocks: Lista de blocos válidos
            
        Returns:
            Dados formatados para o contrato
        """
        batch_id = f"batch_{hash(str([b.block_id for b in blocks])) % 1000000}"
        
        return {
            'batch_id': batch_id,
            'block_ids': [block.block_id for block in blocks],
            'miners': [block.miner for block in blocks],
            'points': [int(block.points * 1000) for block in blocks],  # Converter para wei
            'signatures': [block.signature.encode() for block in blocks]
        }
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas de validação"""
        return self.validation_stats.copy()
