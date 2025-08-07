"""
Sistema de armazenamento local para blocos minerados
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from .models import MiningBlock, BlockStatus


class LocalBlockStorage:
    """Armazenamento local de blocos minerados"""
    
    def __init__(self, blocks_directory: str = "./blocos", backup_enabled: bool = True):
        """
        Inicializa o sistema de armazenamento
        
        Args:
            blocks_directory: Diretório para armazenar blocos
            backup_enabled: Se deve fazer backup dos blocos
        """
        self.blocks_directory = Path(blocks_directory)
        self.backup_enabled = backup_enabled
        
        # Criar diretórios se não existirem
        self.blocks_directory.mkdir(parents=True, exist_ok=True)
        
        if backup_enabled:
            self.backup_directory = self.blocks_directory / "backups"
            self.backup_directory.mkdir(parents=True, exist_ok=True)
    
    def save_block(self, block: MiningBlock) -> str:
        """
        Salva um bloco no armazenamento local
        
        Args:
            block: Bloco para salvar
            
        Returns:
            Caminho do arquivo salvo
        """
        # Nome do arquivo baseado no block_id
        filename = f"{block.block_id}.json"
        file_path = self.blocks_directory / filename
        
        # Converter bloco para dicionário
        block_data = block.to_dict()
        block_data['saved_at'] = datetime.utcnow().isoformat()
        
        # Salvar arquivo
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(block_data, f, indent=2, ensure_ascii=False)
        
        # Fazer backup se habilitado
        if self.backup_enabled:
            backup_path = self.backup_directory / filename
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(block_data, f, indent=2, ensure_ascii=False)
        
        return str(file_path)
    
    def load_block(self, block_id: str) -> Optional[MiningBlock]:
        """
        Carrega um bloco do armazenamento
        
        Args:
            block_id: ID do bloco
            
        Returns:
            Bloco carregado ou None se não encontrado
        """
        filename = f"{block_id}.json"
        file_path = self.blocks_directory / filename
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                block_data = json.load(f)
            
            # Converter de volta para MiningBlock
            return self._dict_to_block(block_data)
            
        except Exception as e:
            print(f"Erro ao carregar bloco {block_id}: {e}")
            return None
    
    def get_blocks_by_status(self, status: BlockStatus) -> List[MiningBlock]:
        """
        Obtém todos os blocos com um status específico
        
        Args:
            status: Status dos blocos
            
        Returns:
            Lista de blocos
        """
        blocks = []
        
        for file_path in self.blocks_directory.glob("*.json"):
            if file_path.name.startswith("backup"):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    block_data = json.load(f)
                
                if block_data.get('block_status') == status.value:
                    block = self._dict_to_block(block_data)
                    if block:
                        blocks.append(block)
                        
            except Exception as e:
                print(f"Erro ao carregar bloco {file_path}: {e}")
                continue
        
        return blocks
    
    def update_block_status(self, block_id: str, new_status: BlockStatus, 
                          tx_hash: Optional[str] = None, 
                          confirmation_block: Optional[int] = None) -> bool:
        """
        Atualiza o status de um bloco
        
        Args:
            block_id: ID do bloco
            new_status: Novo status
            tx_hash: Hash da transação (opcional)
            confirmation_block: Número do bloco de confirmação (opcional)
            
        Returns:
            True se atualização foi bem-sucedida
        """
        block = self.load_block(block_id)
        if not block:
            return False
        
        # Atualizar status
        block.block_status = new_status
        
        if tx_hash:
            block.tx_hash = tx_hash
        
        if confirmation_block:
            block.confirmation_block = confirmation_block
        
        if new_status == BlockStatus.SUBMITTED:
            block.submitted_at = datetime.utcnow()
        
        # Salvar bloco atualizado
        self.save_block(block)
        return True
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do armazenamento"""
        total_blocks = 0
        status_counts = {status.value: 0 for status in BlockStatus}
        total_size = 0
        
        for file_path in self.blocks_directory.glob("*.json"):
            if file_path.name.startswith("backup"):
                continue
                
            try:
                total_size += file_path.stat().st_size
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    block_data = json.load(f)
                
                total_blocks += 1
                status = block_data.get('block_status', 'unknown')
                if status in status_counts:
                    status_counts[status] += 1
                    
            except Exception:
                continue
        
        return {
            'total_blocks': total_blocks,
            'status_counts': status_counts,
            'total_size_bytes': total_size,
            'storage_directory': str(self.blocks_directory),
            'backup_enabled': self.backup_enabled
        }
    
    def _dict_to_block(self, block_data: Dict[str, Any]) -> Optional[MiningBlock]:
        """Converte dicionário de volta para MiningBlock"""
        try:
            # Converter timestamps
            created_at = datetime.fromisoformat(block_data['created_at'])
            mined_at = datetime.fromisoformat(block_data['mined_at']) if block_data.get('mined_at') else None
            submitted_at = datetime.fromisoformat(block_data['submitted_at']) if block_data.get('submitted_at') else None
            
            return MiningBlock(
                block_id=block_data['block_id'],
                event_id=block_data['event_id'],
                status=block_data['status'],
                retries=block_data['retries'],
                fallback_used=block_data['fallback_used'],
                source_system=block_data['source_system'],
                destination=block_data['destination'],
                points=block_data['points'],
                miner=block_data['miner'],
                signature=block_data['signature'],
                public_key=block_data['public_key'],
                payload_hash=block_data['payload_hash'],
                request_duration=block_data['request_duration'],
                response_size=block_data['response_size'],
                created_at=created_at,
                mined_at=mined_at,
                submitted_at=submitted_at,
                block_status=BlockStatus(block_data['block_status']),
                tx_hash=block_data.get('tx_hash'),
                confirmation_block=block_data.get('confirmation_block')
            )
            
        except Exception as e:
            print(f"Erro ao converter dicionário para bloco: {e}")
            return None
