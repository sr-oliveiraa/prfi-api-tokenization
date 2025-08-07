"""
Exemplo básico de uso do PRFI Protocol.

Este exemplo demonstra como usar o PRFI Protocol para fazer requisições
HTTP com retry automático, fallback e tokenização blockchain.
"""

import asyncio
import os
from datetime import datetime

from prfi_core import PRFIClient, PRFIConfig


async def exemplo_basico():
    """Exemplo básico de requisição com PRFI."""
    print("🚀 Exemplo Básico do PRFI Protocol")
    print("=" * 50)
    
    # Configurar cliente
    client = PRFIClient(
        api_key="demo_api_key_123",
        miner_address="0x742d35Cc6634C0532925a3b8D4C9db96590c6C87",  # Endereço de exemplo
        private_key="0x4c0883a69102937d6231471b5dbb6204fe5129617082792ae468d01a3f362318"  # Chave de exemplo (TESTNET)
    )
    
    try:
        # Fazer requisição simples
        print("\n1. Requisição simples (sem retry/fallback)")
        response = await client.request(
            url="https://httpbin.org/status/200",
            method="GET"
        )
        
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📦 Bloco minerado: {response.block_id}")
        print(f"   💰 Pontos ganhos: {response.points_earned}")
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")


async def exemplo_com_retry():
    """Exemplo com retry automático."""
    print("\n2. Requisição com retry automático")
    
    client = PRFIClient(
        api_key="demo_api_key_123",
        miner_address="0x742d35Cc6634C0532925a3b8D4C9db96590c6C87"
    )
    
    try:
        # Simular falha que será resolvida com retry
        response = await client.request(
            url="https://httpbin.org/status/500,500,200",  # Falha 2x, sucesso na 3ª
            method="GET",
            max_retries=3,
            retry_delay=1.0,
            exponential_backoff=True
        )
        
        print(f"   ✅ Status final: {response.status_code}")
        print(f"   🔄 Retries usados: {response.retries_used}")
        print(f"   ⏱️ Tempo total: {response.total_duration:.2f}s")
        print(f"   💰 Pontos ganhos: {response.points_earned}")
        
    except Exception as e:
        print(f"   ❌ Erro após retries: {e}")


async def exemplo_com_fallback():
    """Exemplo com fallback para endpoint alternativo."""
    print("\n3. Requisição com fallback")
    
    client = PRFIClient(
        api_key="demo_api_key_123",
        miner_address="0x742d35Cc6634C0532925a3b8D4C9db96590c6C87"
    )
    
    try:
        # URL principal falha, fallback funciona
        response = await client.request(
            url="https://httpbin.org/status/500",  # Sempre falha
            method="GET",
            fallback_url="https://httpbin.org/get",  # Fallback funciona
            max_retries=2
        )
        
        print(f"   ✅ Status: {response.status_code}")
        print(f"   🔀 Fallback usado: {response.fallback_used}")
        print(f"   🔄 Retries no principal: {response.retries_used}")
        print(f"   💰 Pontos ganhos: {response.points_earned}")
        
    except Exception as e:
        print(f"   ❌ Erro mesmo com fallback: {e}")


async def exemplo_post_com_dados():
    """Exemplo de POST com dados JSON."""
    print("\n4. Requisição POST com dados")
    
    client = PRFIClient(
        api_key="demo_api_key_123",
        miner_address="0x742d35Cc6634C0532925a3b8D4C9db96590c6C87"
    )
    
    try:
        # Dados para enviar
        dados_pedido = {
            "pedido_id": "12345",
            "cliente": "João Silva",
            "valor": 99.90,
            "items": [
                {"produto": "Camiseta", "quantidade": 2, "preco": 29.90},
                {"produto": "Calça", "quantidade": 1, "preco": 39.90}
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        response = await client.request(
            url="https://httpbin.org/post",
            method="POST",
            data=dados_pedido,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": "secret123"
            },
            max_retries=3
        )
        
        print(f"   ✅ Status: {response.status_code}")
        print(f"   📦 Dados enviados: {len(str(dados_pedido))} bytes")
        print(f"   💰 Pontos ganhos: {response.points_earned}")
        
        # Mostrar resposta
        if response.data:
            json_data = response.data.get('json', {})
            print(f"   📄 Pedido processado: {json_data.get('pedido_id')}")
        
    except Exception as e:
        print(f"   ❌ Erro no POST: {e}")


async def exemplo_webhook():
    """Exemplo de envio de webhook com retry."""
    print("\n5. Envio de webhook com retry")
    
    client = PRFIClient(
        api_key="demo_api_key_123",
        miner_address="0x742d35Cc6634C0532925a3b8D4C9db96590c6C87"
    )
    
    try:
        # Dados do webhook
        webhook_data = {
            "event": "pedido.criado",
            "pedido_id": "12345",
            "status": "confirmado",
            "valor": 99.90,
            "timestamp": datetime.now().isoformat(),
            "signature": "sha256=abc123..."
        }
        
        response = await client.request(
            url="https://httpbin.org/post",  # Simular webhook do cliente
            method="POST",
            data=webhook_data,
            headers={
                "Content-Type": "application/json",
                "X-Webhook-Signature": "sha256=abc123...",
                "User-Agent": "PRFI-Webhook/1.0"
            },
            max_retries=5,  # Webhooks precisam de mais retries
            retry_delay=2.0,
            exponential_backoff=True
        )
        
        print(f"   ✅ Webhook enviado: {response.status_code}")
        print(f"   🔄 Tentativas: {response.retries_used + 1}")
        print(f"   💰 Pontos ganhos: {response.points_earned}")
        
    except Exception as e:
        print(f"   ❌ Webhook falhou: {e}")


async def exemplo_multiplas_requisicoes():
    """Exemplo de múltiplas requisições em paralelo."""
    print("\n6. Múltiplas requisições em paralelo")
    
    client = PRFIClient(
        api_key="demo_api_key_123",
        miner_address="0x742d35Cc6634C0532925a3b8D4C9db96590c6C87"
    )
    
    # Lista de URLs para testar
    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/2", 
        "https://httpbin.org/delay/1",
        "https://httpbin.org/status/200",
        "https://httpbin.org/json"
    ]
    
    try:
        # Executar requisições em paralelo
        tasks = []
        for i, url in enumerate(urls):
            task = client.request(
                url=url,
                method="GET",
                max_retries=2
            )
            tasks.append(task)
        
        # Aguardar todas as requisições
        start_time = datetime.now()
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = datetime.now()
        
        # Analisar resultados
        sucessos = 0
        falhas = 0
        total_pontos = 0.0
        
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"   ❌ URL {i+1}: {response}")
                falhas += 1
            else:
                print(f"   ✅ URL {i+1}: Status {response.status_code}, Pontos {response.points_earned}")
                sucessos += 1
                total_pontos += response.points_earned
        
        duration = (end_time - start_time).total_seconds()
        print(f"\n   📊 Resumo:")
        print(f"   ⏱️ Tempo total: {duration:.2f}s")
        print(f"   ✅ Sucessos: {sucessos}")
        print(f"   ❌ Falhas: {falhas}")
        print(f"   💰 Total de pontos: {total_pontos}")
        
    except Exception as e:
        print(f"   ❌ Erro nas requisições paralelas: {e}")


async def exemplo_configuracao_avancada():
    """Exemplo com configuração avançada."""
    print("\n7. Configuração avançada")
    
    # Configuração personalizada
    config = PRFIConfig(
        max_retries=5,
        retry_delay=1.5,
        exponential_backoff=True,
        max_retry_delay=30.0,
        enable_fallback=True,
        enable_tokenization=True,
        blockchain_network="mumbai",  # Testnet
        confirmation_blocks=3,  # Menos confirmações para testnet
        timeout=30.0,
        enable_metrics=True
    )
    
    client = PRFIClient(
        api_key="demo_api_key_123",
        miner_address="0x742d35Cc6634C0532925a3b8D4C9db96590c6C87",
        config=config
    )
    
    try:
        response = await client.request(
            url="https://httpbin.org/delay/2",
            method="GET",
            fallback_url="https://httpbin.org/get"
        )
        
        print(f"   ✅ Requisição com config avançada: {response.status_code}")
        print(f"   ⚙️ Configuração aplicada: max_retries={config.max_retries}")
        print(f"   🌐 Rede blockchain: {config.blockchain_network}")
        print(f"   💰 Pontos ganhos: {response.points_earned}")
        
        # Mostrar métricas se habilitadas
        if config.enable_metrics:
            metrics = client.get_metrics()
            print(f"   📊 Total de requisições: {metrics.get('total_requests', 0)}")
            print(f"   📊 Taxa de sucesso: {metrics.get('success_rate', 0):.1%}")
        
    except Exception as e:
        print(f"   ❌ Erro com config avançada: {e}")


async def main():
    """Função principal que executa todos os exemplos."""
    print("🎯 Exemplos do PRFI Protocol")
    print("Este script demonstra diferentes usos do protocolo PRFI")
    print()
    
    try:
        # Executar exemplos em sequência
        await exemplo_basico()
        await exemplo_com_retry()
        await exemplo_com_fallback()
        await exemplo_post_com_dados()
        await exemplo_webhook()
        await exemplo_multiplas_requisicoes()
        await exemplo_configuracao_avancada()
        
        print("\n" + "=" * 50)
        print("✅ Todos os exemplos executados com sucesso!")
        print()
        print("💡 Próximos passos:")
        print("   1. Verifique os blocos minerados: prfi blocks list")
        print("   2. Submeta para blockchain: prfi submit")
        print("   3. Verifique seu saldo: prfi balance")
        print("   4. Explore outros exemplos na pasta examples/")
        
    except KeyboardInterrupt:
        print("\n⏹️ Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro geral: {e}")
        print("💡 Verifique sua configuração no arquivo .env")


if __name__ == "__main__":
    # Executar exemplos
    asyncio.run(main())
