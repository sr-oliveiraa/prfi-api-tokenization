"""
Exemplo de uso do sistema de mineração de blocos PRFI.

Este exemplo demonstra como:
1. Configurar um minerador
2. Gerar chaves criptográficas
3. Minerar blocos a partir de eventos
4. Consultar estatísticas
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from .crypto import generate_miner_keys
from .miner import create_block_miner, create_miner_config, BlockMiner
from .models import MinerConfig


async def exemplo_mineracao_basica():
    """Exemplo básico de mineração de blocos."""
    print("=== Exemplo de Mineração de Blocos PRFI ===\n")
    
    # 1. Configurar minerador
    miner_id = "miner_001"
    miner_address = "0x1234567890abcdef1234567890abcdef12345678"
    
    print(f"1. Configurando minerador: {miner_id}")
    print(f"   Endereço: {miner_address}")
    
    # 2. Gerar chaves se não existirem
    keys_dir = "./keys"
    private_key_path = f"{keys_dir}/{miner_id}_private.pem"
    public_key_path = f"{keys_dir}/{miner_id}_public.pem"
    
    if not Path(private_key_path).exists():
        print("2. Gerando chaves criptográficas...")
        generate_miner_keys(miner_id, keys_dir)
        print(f"   Chaves salvas em: {keys_dir}")
    else:
        print("2. Usando chaves existentes")
    
    # 3. Criar minerador
    print("3. Inicializando minerador...")
    miner = create_block_miner(
        miner_id=miner_id,
        miner_address=miner_address,
        keys_directory=keys_dir,
        blocks_directory="./blocos",
        base_points=0.4,
        max_blocks_per_hour=1000,
        max_blocks_per_day=5000
    )
    
    # 4. Simular eventos processados
    print("4. Minerando blocos de exemplo...")
    
    eventos_exemplo = [
        {
            "event_id": "evt_001",
            "status": 200,
            "retries": 0,
            "fallback_used": False,
            "source_system": "erp-vendas",
            "destination": "https://api.sefaz.gov.br/nfe",
            "payload": {"nfe_id": "12345", "valor": 1500.00},
            "request_duration": 0.8,
            "response_size": 2048
        },
        {
            "event_id": "evt_002", 
            "status": 200,
            "retries": 2,
            "fallback_used": True,
            "source_system": "crm-leads",
            "destination": "https://webhook.zapier.com/hooks/catch",
            "payload": {"lead_id": "67890", "score": 85},
            "request_duration": 1.2,
            "response_size": 512
        },
        {
            "event_id": "evt_003",
            "status": 200,
            "retries": 1,
            "fallback_used": False,
            "source_system": "ecommerce",
            "destination": "https://api.correios.com.br/tracking",
            "payload": {"order_id": "ORD-001", "tracking": "BR123456789"},
            "request_duration": 0.5,
            "response_size": 1024
        }
    ]
    
    blocos_minerados = []
    
    for i, evento in enumerate(eventos_exemplo, 1):
        print(f"   Minerando evento {i}: {evento['event_id']}")
        
        resultado = await miner.mine_event_block(evento)
        
        if resultado.success:
            print(f"   ✓ Bloco minerado: {resultado.block.block_id}")
            print(f"     Pontos ganhos: {resultado.points_earned}")
            blocos_minerados.append(resultado.block)
        else:
            print(f"   ✗ Erro na mineração: {resultado.error}")
            if resultado.validation_errors:
                for error in resultado.validation_errors:
                    print(f"     - {error}")
    
    print(f"\n5. Blocos minerados com sucesso: {len(blocos_minerados)}")
    
    # 6. Consultar estatísticas
    print("6. Estatísticas do minerador:")
    stats = miner.get_miner_stats()
    
    print(f"   Total de blocos: {stats['storage']['total_blocks']}")
    print(f"   Total de pontos: {stats['storage']['total_points']}")
    print(f"   Blocos pendentes: {stats['storage']['blocks_by_status']['pending']}")
    print(f"   Eventos última hora: {stats['antifraud']['events_last_hour']}")
    
    # 7. Listar blocos pendentes
    print("\n7. Blocos pendentes de submissão:")
    blocos_pendentes = miner.get_pending_blocks()
    
    for bloco in blocos_pendentes:
        print(f"   - {bloco.block_id}: {bloco.points} pontos")
        print(f"     Evento: {bloco.event_id}")
        print(f"     Origem: {bloco.source_system} -> {bloco.destination}")
    
    return miner, blocos_minerados


async def exemplo_validacao_antifraud():
    """Exemplo de validação anti-fraude."""
    print("\n=== Exemplo de Validação Anti-Fraude ===\n")
    
    # Criar minerador com regras restritivas
    miner_id = "miner_test"
    miner_address = "0xtest1234567890abcdef1234567890abcdef"
    
    # Gerar chaves se necessário
    keys_dir = "./keys"
    if not Path(f"{keys_dir}/{miner_id}_private.pem").exists():
        generate_miner_keys(miner_id, keys_dir)
    
    # Configuração com limites baixos para demonstrar anti-fraude
    config = create_miner_config(
        miner_id=miner_id,
        miner_address=miner_address,
        private_key_path=f"{keys_dir}/{miner_id}_private.pem",
        public_key_path=f"{keys_dir}/{miner_id}_public.pem",
        max_blocks_per_hour=5,  # Limite baixo para teste
        max_blocks_per_day=10,
        min_request_duration=0.5  # Mínimo alto para teste
    )
    
    miner = BlockMiner(config)
    
    # Tentar minerar muitos eventos rapidamente
    print("1. Testando limite de eventos por hora...")
    
    for i in range(7):  # Mais que o limite de 5
        evento = {
            "event_id": f"spam_{i:03d}",
            "status": 200,
            "source_system": "spam-system",
            "destination": "https://api.example.com",
            "payload": {"test": i},
            "request_duration": 0.6
        }
        
        resultado = await miner.mine_event_block(evento)
        
        if resultado.success:
            print(f"   ✓ Evento {i+1}: Minerado")
        else:
            print(f"   ✗ Evento {i+1}: {resultado.error}")
            if resultado.validation_errors:
                for error in resultado.validation_errors:
                    print(f"     - {error}")
    
    # Testar requisições muito rápidas
    print("\n2. Testando requisições suspeitas (muito rápidas)...")
    
    evento_rapido = {
        "event_id": "fast_001",
        "status": 200,
        "source_system": "fast-system",
        "destination": "https://api.example.com",
        "payload": {"test": "fast"},
        "request_duration": 0.01  # Muito rápido
    }
    
    resultado = await miner.mine_event_block(evento_rapido)
    
    if resultado.success:
        print(f"   ✓ Evento rápido: Minerado (pontos: {resultado.points_earned})")
    else:
        print(f"   ✗ Evento rápido: {resultado.error}")
    
    # Testar payload duplicado
    print("\n3. Testando payload duplicado...")
    
    evento_original = {
        "event_id": "dup_001",
        "status": 200,
        "source_system": "dup-system",
        "destination": "https://api.example.com",
        "payload": {"unique": "data123"},
        "request_duration": 0.8
    }
    
    evento_duplicado = {
        "event_id": "dup_002",  # ID diferente
        "status": 200,
        "source_system": "dup-system",
        "destination": "https://api.example.com",
        "payload": {"unique": "data123"},  # Mesmo payload
        "request_duration": 0.8
    }
    
    # Minerar original
    resultado1 = await miner.mine_event_block(evento_original)
    print(f"   Evento original: {'✓' if resultado1.success else '✗'}")
    
    # Tentar minerar duplicado
    resultado2 = await miner.mine_event_block(evento_duplicado)
    print(f"   Evento duplicado: {'✓' if resultado2.success else '✗'}")
    
    if not resultado2.success:
        print(f"     Motivo: {resultado2.error}")


def exemplo_configuracao_avancada():
    """Exemplo de configuração avançada do minerador."""
    print("\n=== Exemplo de Configuração Avançada ===\n")
    
    # Configuração personalizada
    config = MinerConfig(
        miner_id="miner_advanced",
        miner_address="0xadvanced1234567890abcdef1234567890ab",
        private_key_path="./keys/miner_advanced_private.pem",
        public_key_path="./keys/miner_advanced_public.pem",
        
        # Pontuação personalizada
        min_points_per_block=0.1,
        max_points_per_block=2.0,
        base_points=0.5,
        
        # Limites anti-fraude
        max_blocks_per_hour=2000,
        max_blocks_per_day=10000,
        min_request_duration=0.05,
        
        # Storage
        blocks_directory="./blocos_advanced",
        backup_enabled=True
    )
    
    print("Configuração avançada criada:")
    print(f"  Minerador: {config.miner_id}")
    print(f"  Pontos base: {config.base_points}")
    print(f"  Limite/hora: {config.max_blocks_per_hour}")
    print(f"  Diretório: {config.blocks_directory}")
    print(f"  Backup: {config.backup_enabled}")


async def main():
    """Função principal com todos os exemplos."""
    try:
        # Exemplo básico
        miner, blocos = await exemplo_mineracao_basica()
        
        # Exemplo anti-fraude
        await exemplo_validacao_antifraud()
        
        # Exemplo configuração
        exemplo_configuracao_avancada()
        
        print("\n=== Exemplos concluídos com sucesso! ===")
        
    except Exception as e:
        print(f"\nErro nos exemplos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
