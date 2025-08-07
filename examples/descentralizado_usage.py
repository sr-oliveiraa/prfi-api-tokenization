#!/usr/bin/env python3
"""
Exemplo de uso do PRFI Protocol Descentralizado
Sistema sem minter central - cada empresa minera seus próprios tokens
"""

import asyncio
import os
from eth_account import Account
from prfi_core.cliente_descentralizado import PRFIClientDescentralizado


async def exemplo_basico():
    """Exemplo básico de uso descentralizado"""
    print("🚀 PRFI Protocol Descentralizado - Exemplo Básico")
    print("=" * 60)
    
    # Configuração (use suas próprias chaves)
    PRIVATE_KEY = os.getenv('COMPANY_PRIVATE_KEY', '0x' + '1' * 64)  # SUBSTITUA pela sua chave
    CONTRACT_ADDRESS = os.getenv('PRFIC_CONTRACT_ADDRESS', '0x' + '2' * 40)  # SUBSTITUA pelo endereço do contrato
    RPC_URL = os.getenv('POLYGON_RPC_URL', 'https://polygon-rpc.com')
    
    # Criar cliente descentralizado
    client = PRFIClientDescentralizado(
        company_private_key=PRIVATE_KEY,
        contract_address=CONTRACT_ADDRESS,
        rpc_url=RPC_URL,
        min_difficulty=4  # Dificuldade mínima para mineração
    )
    
    print(f"📍 Endereço da empresa: {client.company_address}")
    print(f"📄 Contrato PRFIC: {CONTRACT_ADDRESS}")
    print()
    
    # 1. Registrar empresa (se necessário)
    print("1️⃣ Registrando empresa...")
    registered = await client.register_company("Minha Empresa PRFI")
    
    if registered:
        print("✅ Empresa registrada com sucesso!")
    else:
        print("❌ Falha ao registrar empresa")
        return
    
    print()
    
    # 2. Verificar estatísticas iniciais
    print("2️⃣ Estatísticas iniciais:")
    stats = await client.get_company_stats()
    print(f"   📊 Eventos processados: {stats['events']}")
    print(f"   💰 Tokens PRFIC: {stats['tokens']}")
    print(f"   ✅ Registrada: {stats['registered']}")
    print(f"   🏷️  Nome: {stats['name']}")
    print()
    
    # 3. Fazer requisições com mineração automática
    print("3️⃣ Fazendo requisições com mineração automática...")
    
    urls_teste = [
        "https://httpbin.org/status/200",
        "https://httpbin.org/json",
        "https://httpbin.org/uuid",
        "https://httpbin.org/ip"
    ]
    
    for i, url in enumerate(urls_teste, 1):
        print(f"\n🌐 Requisição {i}: {url}")
        
        response = await client.request(
            url=url,
            method="GET",
            fallback_url="https://httpbin.org/get"  # Fallback
        )
        
        if response.success:
            print(f"   ✅ Sucesso! Status: {response.status_code}")
            print(f"   ⏱️  Tempo: {response.response_time:.2f}s")
            print(f"   🔄 Retries: {response.retries_used}")
            print(f"   🔀 Fallback: {response.fallback_used}")
            print(f"   ⛏️  Mineração iniciada automaticamente...")
        else:
            print(f"   ❌ Falha! Status: {response.status_code}")
    
    print()
    
    # 4. Verificar estatísticas finais
    print("4️⃣ Estatísticas finais:")
    
    # Estatísticas blockchain
    blockchain_stats = await client.get_company_stats()
    print("   📊 Blockchain:")
    print(f"      Eventos: {blockchain_stats['events']}")
    print(f"      Tokens: {blockchain_stats['tokens']}")
    print(f"      Último nonce: {blockchain_stats['nonce']}")
    
    # Estatísticas locais
    local_stats = client.get_local_stats()
    print("   💻 Local:")
    print(f"      Requisições totais: {local_stats['total_requests']}")
    print(f"      Requisições bem-sucedidas: {local_stats['successful_requests']}")
    print(f"      Taxa de sucesso: {local_stats['success_rate']:.1f}%")
    print(f"      Tokens estimados: {local_stats['tokens_earned']:.2f} PRFIC")
    print(f"      Blocos minerados: {local_stats['blocks_mined']}")
    
    print("\n🎉 Exemplo concluído!")


async def exemplo_ecommerce_descentralizado():
    """Exemplo de e-commerce com sistema descentralizado"""
    print("\n🛒 PRFI Protocol Descentralizado - E-commerce")
    print("=" * 60)
    
    # Configuração
    PRIVATE_KEY = os.getenv('COMPANY_PRIVATE_KEY', '0x' + '1' * 64)
    CONTRACT_ADDRESS = os.getenv('PRFIC_CONTRACT_ADDRESS', '0x' + '2' * 40)
    RPC_URL = os.getenv('POLYGON_RPC_URL', 'https://polygon-rpc.com')
    
    client = PRFIClientDescentralizado(
        company_private_key=PRIVATE_KEY,
        contract_address=CONTRACT_ADDRESS,
        rpc_url=RPC_URL,
        min_difficulty=3  # Dificuldade menor para exemplo
    )
    
    # Registrar como loja
    await client.register_company("Loja Virtual PRFI")
    
    # Simular processamento de pedido
    pedido = {
        "id": "PED-12345",
        "cliente": "cliente@email.com",
        "valor": 299.99,
        "produtos": [
            {"id": "PROD-001", "nome": "Produto A", "preco": 149.99},
            {"id": "PROD-002", "nome": "Produto B", "preco": 149.99}
        ]
    }
    
    print(f"📦 Processando pedido: {pedido['id']}")
    
    # 1. Validar pedido
    print("\n1️⃣ Validando pedido...")
    response = await client.request(
        url="https://httpbin.org/post",
        method="POST",
        data={"action": "validate_order", "order": pedido},
        fallback_url="https://httpbin.org/anything"
    )
    
    if response.success:
        print("   ✅ Pedido validado!")
    
    # 2. Processar pagamento
    print("\n2️⃣ Processando pagamento...")
    response = await client.request(
        url="https://httpbin.org/post",
        method="POST",
        data={
            "action": "process_payment",
            "order_id": pedido["id"],
            "amount": pedido["valor"]
        },
        fallback_url="https://httpbin.org/anything"
    )
    
    if response.success:
        print("   💳 Pagamento processado!")
    
    # 3. Atualizar estoque
    print("\n3️⃣ Atualizando estoque...")
    for produto in pedido["produtos"]:
        response = await client.request(
            url="https://httpbin.org/put",
            method="PUT",
            data={
                "action": "update_stock",
                "product_id": produto["id"],
                "quantity": -1
            },
            fallback_url="https://httpbin.org/anything"
        )
        
        if response.success:
            print(f"   📦 Estoque atualizado para {produto['nome']}")
    
    # 4. Enviar confirmação
    print("\n4️⃣ Enviando confirmação...")
    response = await client.request(
        url="https://httpbin.org/post",
        method="POST",
        data={
            "action": "send_confirmation",
            "order_id": pedido["id"],
            "customer_email": pedido["cliente"]
        },
        fallback_url="https://httpbin.org/anything"
    )
    
    if response.success:
        print("   📧 Confirmação enviada!")
    
    # Estatísticas finais
    print("\n📊 Estatísticas do processamento:")
    stats = client.get_local_stats()
    print(f"   Requisições: {stats['total_requests']}")
    print(f"   Sucesso: {stats['success_rate']:.1f}%")
    print(f"   Tokens estimados: {stats['tokens_earned']:.2f} PRFIC")
    print(f"   Blocos minerados: {stats['blocks_mined']}")


async def exemplo_mineracao_manual():
    """Exemplo de mineração manual de blocos"""
    print("\n⛏️  PRFI Protocol - Mineração Manual")
    print("=" * 60)
    
    # Configuração
    PRIVATE_KEY = os.getenv('COMPANY_PRIVATE_KEY', '0x' + '1' * 64)
    CONTRACT_ADDRESS = os.getenv('PRFIC_CONTRACT_ADDRESS', '0x' + '2' * 40)
    
    client = PRFIClientDescentralizado(
        company_private_key=PRIVATE_KEY,
        contract_address=CONTRACT_ADDRESS,
        rpc_url="https://polygon-rpc.com",
        min_difficulty=2  # Dificuldade baixa para exemplo
    )
    
    print(f"🏭 Minerador: {client.company_address}")
    
    # Simular eventos processados
    eventos = [
        {"id": "EVT-001", "tipo": "webhook", "status": 200},
        {"id": "EVT-002", "tipo": "api_call", "status": 200},
        {"id": "EVT-003", "tipo": "notification", "status": 200}
    ]
    
    print(f"📋 Eventos para processar: {len(eventos)}")
    
    # Minerar bloco manualmente
    batch_id = f"BATCH-{int(asyncio.get_event_loop().time())}"
    merkle_root = client._calculate_merkle_root(eventos)
    
    print(f"\n🔨 Iniciando mineração manual...")
    print(f"   Batch ID: {batch_id}")
    print(f"   Merkle Root: {merkle_root}")
    print(f"   Dificuldade mínima: {client.min_difficulty}")
    
    # Minerar
    result = await client._mine_block(
        batch_id=batch_id,
        events_count=1000,
        merkle_root=merkle_root
    )
    
    if result:
        print(f"\n✅ Bloco minerado com sucesso!")
        print(f"   Nonce: {result.nonce}")
        print(f"   Hash: {result.block_hash}")
        print(f"   Dificuldade: {result.difficulty}")
        print(f"   Tempo: {result.mining_time:.2f}s")
        
        # Submeter para blockchain
        print(f"\n📤 Submetendo para blockchain...")
        success = await client._submit_block_to_blockchain(
            batch_id=batch_id,
            events_count=1000,
            nonce=result.nonce,
            merkle_root=merkle_root
        )
        
        if success:
            print("🎉 Bloco confirmado na blockchain!")
        else:
            print("❌ Falha ao submeter bloco")
    else:
        print("❌ Falha na mineração")


async def gerar_chaves_exemplo():
    """Gerar chaves para exemplo"""
    print("\n🔑 Gerando chaves para exemplo...")
    print("=" * 60)
    
    # Gerar nova conta
    account = Account.create()
    
    print("📋 Configuração para .env:")
    print(f"COMPANY_PRIVATE_KEY={account.privateKey.hex()}")
    print(f"COMPANY_ADDRESS={account.address}")
    print()
    print("⚠️  IMPORTANTE:")
    print("   - Use apenas para testes!")
    print("   - Nunca compartilhe a chave privada!")
    print("   - Gere novas chaves para produção!")
    print("   - Adicione MATIC para gas fees!")


async def main():
    """Função principal com menu de exemplos"""
    print("🌟 PRFI Protocol Descentralizado - Exemplos")
    print("=" * 60)
    print()
    print("Escolha um exemplo:")
    print("1. Exemplo básico")
    print("2. E-commerce descentralizado")
    print("3. Mineração manual")
    print("4. Gerar chaves para teste")
    print("0. Sair")
    print()
    
    try:
        opcao = input("Digite sua opção (0-4): ").strip()
        
        if opcao == "1":
            await exemplo_basico()
        elif opcao == "2":
            await exemplo_ecommerce_descentralizado()
        elif opcao == "3":
            await exemplo_mineracao_manual()
        elif opcao == "4":
            await gerar_chaves_exemplo()
        elif opcao == "0":
            print("👋 Até logo!")
        else:
            print("❌ Opção inválida!")
            
    except KeyboardInterrupt:
        print("\n\n👋 Exemplo interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")


if __name__ == "__main__":
    # Verificar configuração
    if not os.getenv('COMPANY_PRIVATE_KEY'):
        print("⚠️  Configure COMPANY_PRIVATE_KEY no .env")
        print("   Execute a opção 4 para gerar chaves de teste")
        print()
    
    if not os.getenv('PRFIC_CONTRACT_ADDRESS'):
        print("⚠️  Configure PRFIC_CONTRACT_ADDRESS no .env")
        print("   Faça o deploy do contrato primeiro")
        print()
    
    # Executar exemplos
    asyncio.run(main())
