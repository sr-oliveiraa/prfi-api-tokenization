"""
Minerador principal de blocos PRFI.

Implementa o sistema de mineração que:
- Recebe eventos processados com sucesso
- Calcula pontos PRFIC baseado em regras
- Aplica validações anti-fraude
- Assina digitalmente os blocos
- Armazena localmente para submissão
"""

import hashlib
import time
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

import structlog

from .models import MiningBlock, MiningResult, MinerConfig, AntifraudRules, BlockStatus
from .crypto import DigitalSigner, create_digital_signer
from .antifraud import AntifraudEngine
from .storage import LocalBlockStorage

logger = structlog.get_logger(__name__)


class BlockMiner:
    """Minerador principal de blocos PRFI."""
    
    def __init__(self, config: MinerConfig):
        """
        Inicializa o minerador.
        
        Args:
            config: Configuração do minerador
        """
        self.config = config
        self.logger = logger.bind(
            component="block_miner",
            miner_id=config.miner_id
        )
        
        # Inicializar componentes
        self.signer = DigitalSigner(
            config.private_key_path,
            config.public_key_path
        )
        
        # Regras anti-fraude padrão
        antifraud_rules = AntifraudRules(
            max_events_per_hour=config.max_blocks_per_hour,
            max_events_per_day=config.max_blocks_per_day,
            min_request_duration=config.min_request_duration,
            max_points_per_event=config.max_points_per_block
        )
        
        self.antifraud = AntifraudEngine(antifraud_rules)
        self.storage = LocalBlockStorage(
            config.blocks_directory,
            config.backup_enabled
        )
        
        self.logger.info("Minerador inicializado com sucesso")
    
    async def mine_event_block(self, event_data: Dict[str, Any]) -> MiningResult:
        """
        Minera um bloco a partir de um evento processado.
        
        Args:
            event_data: Dados do evento PRFI processado
            
        Returns:
            Resultado da mineração
        """
        try:
            # Validar dados de entrada
            validation_errors = self._validate_event_data(event_data)
            if validation_errors:
                return MiningResult(
                    success=False,
                    error="Dados de evento inválidos",
                    validation_errors=validation_errors
                )
            
            # Calcular pontos PRFIC
            points = self._calculate_points(event_data)
            
            # Criar hash do payload
            payload_hash = self._create_payload_hash(event_data.get('payload', {}))
            
            # Criar bloco
            block = MiningBlock(
                event_id=event_data['event_id'],
                status=event_data['status'],
                retries=event_data.get('retries', 0),
                fallback_used=event_data.get('fallback_used', False),
                source_system=event_data['source_system'],
                destination=event_data['destination'],
                points=points,
                miner=self.config.miner_address,
                signature="",  # Será preenchida após assinatura
                public_key=self.signer.get_public_key_string(),
                payload_hash=payload_hash,
                request_duration=event_data.get('request_duration', 0.0),
                response_size=event_data.get('response_size', 0)
            )
            
            # Validar contra regras anti-fraude
            is_valid, fraud_errors = self.antifraud.validate_block(block)
            if not is_valid:
                return MiningResult(
                    success=False,
                    error="Bloco rejeitado pelas regras anti-fraude",
                    validation_errors=fraud_errors
                )
            
            # Assinar bloco
            signing_data = block.get_signing_data()
            signature = self.signer.sign_data(signing_data)
            block.signature = signature
            
            # Salvar bloco
            file_path = self.storage.save_block(block)
            
            self.logger.info(
                "Bloco minerado com sucesso",
                block_id=block.block_id,
                event_id=block.event_id,
                points=points,
                file_path=file_path
            )
            
            return MiningResult(
                success=True,
                block=block,
                points_earned=points
            )
            
        except Exception as e:
            self.logger.error(
                "Erro na mineração de bloco",
                event_id=event_data.get('event_id', 'unknown'),
                error=str(e)
            )
            
            return MiningResult(
                success=False,
                error=f"Erro interno: {str(e)}"
            )
    
    def _validate_event_data(self, event_data: Dict[str, Any]) -> list[str]:
        """Valida dados de entrada do evento."""
        errors = []
        
        required_fields = [
            'event_id', 'status', 'source_system', 'destination'
        ]
        
        for field in required_fields:
            if field not in event_data:
                errors.append(f"Campo obrigatório ausente: {field}")
        
        # Validar status
        if 'status' in event_data and event_data['status'] != 200:
            errors.append(f"Status deve ser 200, recebido: {event_data['status']}")
        
        # Validar tipos
        if 'retries' in event_data and not isinstance(event_data['retries'], int):
            errors.append("Campo 'retries' deve ser inteiro")
        
        if 'fallback_used' in event_data and not isinstance(event_data['fallback_used'], bool):
            errors.append("Campo 'fallback_used' deve ser booleano")
        
        if 'request_duration' in event_data:
            try:
                float(event_data['request_duration'])
            except (ValueError, TypeError):
                errors.append("Campo 'request_duration' deve ser numérico")
        
        return errors
    
    def _calculate_points(self, event_data: Dict[str, Any]) -> float:
        """
        Calcula pontos PRFIC para um evento.
        
        Regras de pontuação:
        - Base: 0.4 pontos por evento bem-sucedido
        - Bônus por retry: +0.1 por tentativa adicional (máx 0.3)
        - Bônus por fallback: +0.2 se fallback foi usado
        - Penalidade por duração: -0.1 se muito rápido (< 0.1s)
        """
        points = self.config.base_points
        
        # Bônus por retries (indica resiliência)
        retries = event_data.get('retries', 0)
        retry_bonus = min(retries * 0.1, 0.3)
        points += retry_bonus
        
        # Bônus por uso de fallback
        if event_data.get('fallback_used', False):
            points += 0.2
        
        # Penalidade por requisições muito rápidas (possível fraude)
        request_duration = event_data.get('request_duration', 0.0)
        if request_duration < 0.1:
            points -= 0.1
        
        # Aplicar limites
        points = max(self.config.min_points_per_block, points)
        points = min(self.config.max_points_per_block, points)
        
        return round(points, 3)
    
    def _create_payload_hash(self, payload: Dict[str, Any]) -> str:
        """Cria hash SHA-256 do payload."""
        import json
        payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(payload_json.encode('utf-8')).hexdigest()
    
    def get_pending_blocks(self) -> list[MiningBlock]:
        """Obtém blocos pendentes de submissão."""
        return self.storage.get_blocks_by_status(BlockStatus.PENDING)
    
    def get_miner_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do minerador."""
        storage_stats = self.storage.get_storage_stats()
        antifraud_stats = self.antifraud.get_miner_stats(self.config.miner_address)
        
        return {
            "miner_id": self.config.miner_id,
            "miner_address": self.config.miner_address,
            "storage": storage_stats,
            "antifraud": antifraud_stats,
            "config": {
                "base_points": self.config.base_points,
                "max_blocks_per_hour": self.config.max_blocks_per_hour,
                "max_blocks_per_day": self.config.max_blocks_per_day
            }
        }
    
    def update_block_status(self, block_id: str, new_status: BlockStatus,
                           tx_hash: Optional[str] = None,
                           confirmation_block: Optional[int] = None) -> bool:
        """
        Atualiza status de um bloco.
        
        Args:
            block_id: ID do bloco
            new_status: Novo status
            tx_hash: Hash da transação (opcional)
            confirmation_block: Número do bloco de confirmação (opcional)
            
        Returns:
            True se atualização foi bem-sucedida
        """
        return self.storage.update_block_status(
            block_id, new_status, tx_hash, confirmation_block
        )


def create_miner_config(
    miner_id: str,
    miner_address: str,
    private_key_path: str,
    public_key_path: str,
    **kwargs
) -> MinerConfig:
    """
    Função de conveniência para criar configuração de minerador.
    
    Args:
        miner_id: ID único do minerador
        miner_address: Endereço/wallet do minerador
        private_key_path: Caminho para chave privada
        public_key_path: Caminho para chave pública
        **kwargs: Parâmetros adicionais
        
    Returns:
        Configuração do minerador
    """
    return MinerConfig(
        miner_id=miner_id,
        miner_address=miner_address,
        private_key_path=private_key_path,
        public_key_path=public_key_path,
        **kwargs
    )


def create_block_miner(
    miner_id: str,
    miner_address: str,
    keys_directory: str = "./keys",
    blocks_directory: str = "./blocos",
    **kwargs
) -> BlockMiner:
    """
    Função de conveniência para criar minerador de blocos.
    
    Args:
        miner_id: ID único do minerador
        miner_address: Endereço/wallet do minerador
        keys_directory: Diretório das chaves
        blocks_directory: Diretório dos blocos
        **kwargs: Parâmetros adicionais
        
    Returns:
        Minerador configurado
    """
    private_key_path = f"{keys_directory}/{miner_id}_private.pem"
    public_key_path = f"{keys_directory}/{miner_id}_public.pem"
    
    config = create_miner_config(
        miner_id=miner_id,
        miner_address=miner_address,
        private_key_path=private_key_path,
        public_key_path=public_key_path,
        blocks_directory=blocks_directory,
        **kwargs
    )
    
    return BlockMiner(config)
