"""
Exemplo de uso do sistema de submissão PRFI.

Este exemplo demonstra como usar o submitter para processar blocos pendentes
e submetê-los para a blockchain Polygon.
"""

import asyncio
import os
from datetime import datetime

from submitter import (
    BlockSubmitter,
    SubmissionConfig,
    BlockScanner,
    SubmissionValidator,
    BlockBatcher
)


async def exemplo_submissao_basica():
    """Exemplo básico de submissão de blocos."""
    print("=== Exemplo de Submissão Básica ===")
    
    # Configuração do submitter
    config = SubmissionConfig(
        # Blockchain
        rpc_url="https://polygon-rpc.com",  # Polygon mainnet
        contract_address="0x1234567890123456789012345678901234567890",  # Endereço do contrato PRFIC
        private_key="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",  # Sua chave privada
        chain_id=137,  # Polygon mainnet
        
        # Batching
        batch_size=5,
        max_batch_size=20,
        min_batch_size=1,
        
        # Gas
        gas_limit=500000,
        gas_price_multiplier=1.1,
        max_gas_price=100000000000,  # 100 gwei
        
        # Retry
        max_retries=3,
        retry_delay=60,
        
        # Diretórios
        blocks_directory="./blocos",
        logs_directory="./logs"
    )
    
    # Criar submitter
    submitter = BlockSubmitter(config)
    
    try:
        # Processar blocos pendentes
        print("Processando blocos pendentes...")
        results = await submitter.process_pending_blocks()
        
        # Mostrar resultados
        print(f"\nResultados da submissão:")
        for result in results:
            if result.success:
                print(f"✅ Batch {result.batch_id}: {result.blocks_submitted} blocos, {result.points_submitted} pontos")
                print(f"   TX Hash: {result.tx_hash}")
            else:
                print(f"❌ Batch {result.batch_id}: {result.error}")
                if result.retry_scheduled:
                    print(f"   Retry agendado")
        
        # Mostrar estatísticas
        stats = submitter.get_stats()
        print(f"\nEstatísticas:")
        print(f"- Blockchain conectada: {stats['blockchain']['connected']}")
        print(f"- Último bloco: {stats['blockchain']['latest_block']}")
        print(f"- Blocos pendentes: {stats['scanner']['total_pending']}")
        
    except Exception as e:
        print(f"Erro na submissão: {e}")


async def exemplo_processamento_continuo():
    """Exemplo de processamento contínuo."""
    print("\n=== Exemplo de Processamento Contínuo ===")
    
    config = SubmissionConfig(
        rpc_url="https://polygon-rpc.com",
        contract_address="0x1234567890123456789012345678901234567890",
        private_key="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        batch_size=10,
        blocks_directory="./blocos"
    )
    
    submitter = BlockSubmitter(config)
    
    print("Iniciando processamento contínuo (pressione Ctrl+C para parar)...")
    
    try:
        # Processar a cada 2 minutos
        await submitter.start_continuous_processing(interval=120)
    except KeyboardInterrupt:
        print("\nParando processamento contínuo...")
        submitter.stop_continuous_processing()


async def exemplo_componentes_individuais():
    """Exemplo usando componentes individuais."""
    print("\n=== Exemplo de Componentes Individuais ===")
    
    config = SubmissionConfig(
        rpc_url="https://polygon-rpc.com",
        contract_address="0x1234567890123456789012345678901234567890",
        private_key="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        blocks_directory="./blocos"
    )
    
    # 1. Scanner - encontrar blocos pendentes
    scanner = BlockScanner(config)
    pending_blocks = scanner.scan_pending_blocks()
    print(f"Blocos pendentes encontrados: {len(pending_blocks)}")
    
    if not pending_blocks:
        print("Nenhum bloco pendente para processar")
        return
    
    # 2. Validator - validar blocos
    validator = SubmissionValidator(config)
    valid_blocks, errors = validator.validate_blocks(pending_blocks)
    print(f"Blocos válidos: {len(valid_blocks)}")
    if errors:
        print(f"Erros de validação: {len(errors)}")
        for error in errors[:3]:  # Mostrar apenas os primeiros 3
            print(f"  - {error}")
    
    if not valid_blocks:
        print("Nenhum bloco válido para submissão")
        return
    
    # 3. Batcher - criar batches
    batcher = BlockBatcher(config)
    batches = batcher.create_batches(valid_blocks)
    print(f"Batches criados: {len(batches)}")
    
    for i, batch in enumerate(batches):
        print(f"  Batch {i+1}: {len(batch.blocks)} blocos, {batch.total_points} pontos")
    
    # 4. Submitter - submeter batches
    submitter = BlockSubmitter(config)
    
    for batch in batches:
        print(f"\nSubmetendo batch {batch.batch_id}...")
        result = await submitter.submit_batch(batch)
        
        if result.success:
            print(f"✅ Sucesso: TX {result.tx_hash}")
        else:
            print(f"❌ Falha: {result.error}")


async def exemplo_monitoramento():
    """Exemplo de monitoramento de transações."""
    print("\n=== Exemplo de Monitoramento ===")
    
    config = SubmissionConfig(
        rpc_url="https://polygon-rpc.com",
        contract_address="0x1234567890123456789012345678901234567890",
        private_key="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        blocks_directory="./blocos"
    )
    
    submitter = BlockSubmitter(config)
    
    # Monitorar confirmações
    print("Monitorando confirmações de transações...")
    await submitter.monitor_confirmations()
    
    # Obter estatísticas do monitor
    stats = submitter.get_stats()
    if 'monitor' in stats:
        monitor_stats = stats['monitor']
        print(f"Transações monitoradas: {monitor_stats.get('monitored_transactions', 0)}")
        print(f"Tempo médio de confirmação: {monitor_stats.get('avg_confirmation_time', 0):.1f}s")


def exemplo_configuracao_avancada():
    """Exemplo de configuração avançada."""
    print("\n=== Exemplo de Configuração Avançada ===")
    
    # Configuração para ambiente de desenvolvimento
    dev_config = SubmissionConfig(
        # Testnet Polygon Mumbai
        rpc_url="https://rpc-mumbai.maticvigil.com",
        contract_address="0x...",  # Endereço do contrato na testnet
        private_key=os.getenv("PRIVATE_KEY_TESTNET"),
        chain_id=80001,  # Mumbai testnet
        
        # Batching otimizado para desenvolvimento
        batch_size=3,
        max_batch_size=10,
        min_batch_size=1,
        
        # Gas conservador para testnet
        gas_limit=300000,
        gas_price_multiplier=1.0,
        max_gas_price=50000000000,  # 50 gwei
        
        # Retry agressivo para testes
        max_retries=5,
        retry_delay=30,
        exponential_backoff=True,
        
        # Confirmações rápidas para desenvolvimento
        confirmation_blocks=3,
        poll_interval=15,
        
        # Otimizações habilitadas
        enable_gas_optimization=True,
        enable_batch_optimization=True,
        parallel_submissions=1,
        
        # Diretórios específicos
        blocks_directory="./test_blocos",
        logs_directory="./test_logs"
    )
    
    print("Configuração de desenvolvimento criada:")
    print(f"- RPC: {dev_config.rpc_url}")
    print(f"- Chain ID: {dev_config.chain_id}")
    print(f"- Batch size: {dev_config.batch_size}")
    print(f"- Gas limit: {dev_config.gas_limit}")
    print(f"- Max retries: {dev_config.max_retries}")
    
    # Configuração para produção
    prod_config = SubmissionConfig(
        # Mainnet Polygon
        rpc_url="https://polygon-rpc.com",
        contract_address=os.getenv("PRFIC_CONTRACT_ADDRESS"),
        private_key=os.getenv("PRIVATE_KEY_MAINNET"),
        chain_id=137,
        
        # Batching otimizado para produção
        batch_size=20,
        max_batch_size=50,
        min_batch_size=5,
        
        # Gas otimizado para mainnet
        gas_limit=800000,
        gas_price_multiplier=1.2,
        max_gas_price=200000000000,  # 200 gwei
        
        # Retry conservador para produção
        max_retries=3,
        retry_delay=120,
        exponential_backoff=True,
        
        # Confirmações seguras para produção
        confirmation_blocks=12,
        poll_interval=60,
        
        # Todas as otimizações habilitadas
        enable_gas_optimization=True,
        enable_batch_optimization=True,
        parallel_submissions=2,
        
        # Diretórios de produção
        blocks_directory="/var/prfi/blocos",
        logs_directory="/var/prfi/logs"
    )
    
    print("\nConfiguração de produção criada:")
    print(f"- RPC: {prod_config.rpc_url}")
    print(f"- Chain ID: {prod_config.chain_id}")
    print(f"- Batch size: {prod_config.batch_size}")
    print(f"- Gas limit: {prod_config.gas_limit}")
    print(f"- Max retries: {prod_config.max_retries}")


async def main():
    """Função principal com todos os exemplos."""
    print("🚀 Exemplos do Sistema de Submissão PRFI")
    print("=" * 50)
    
    # Verificar se as variáveis de ambiente estão configuradas
    if not os.getenv("PRIVATE_KEY_TESTNET"):
        print("⚠️  Configure as variáveis de ambiente:")
        print("   export PRIVATE_KEY_TESTNET=0x...")
        print("   export PRIVATE_KEY_MAINNET=0x...")
        print("   export PRFIC_CONTRACT_ADDRESS=0x...")
        print()
    
    try:
        # Executar exemplos
        await exemplo_submissao_basica()
        await exemplo_componentes_individuais()
        await exemplo_monitoramento()
        exemplo_configuracao_avancada()
        
        # Exemplo de processamento contínuo (comentado para não bloquear)
        # await exemplo_processamento_continuo()
        
    except Exception as e:
        print(f"❌ Erro nos exemplos: {e}")
    
    print("\n✅ Exemplos concluídos!")


if __name__ == "__main__":
    # Executar exemplos
    asyncio.run(main())
