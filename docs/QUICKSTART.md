# ⚡ Guia de Início Rápido PRFI Protocol

Este guia te ajudará a começar a usar o PRFI Protocol em **menos de 10 minutos**.

## 🎯 O que você vai aprender

- ✅ Instalar o PRFI Protocol
- ✅ Configurar sua primeira integração
- ✅ Fazer sua primeira requisição com retry/fallback
- ✅ Minerar seu primeiro bloco
- ✅ Ganhar seus primeiros tokens PRFIC

## 📋 Pré-requisitos

- Python 3.8+
- Conta na Polygon (Metamask)
- 5 minutos do seu tempo

## 🚀 Passo 1: Instalação

```bash
# Instalar PRFI Protocol
pip install prfi-protocol

# Verificar instalação
prfi --version
```

## 🔧 Passo 2: Configuração Básica

### Criar arquivo de configuração

```bash
# Criar arquivo .env
cat > .env << EOF
# Testnet para começar (sem custos)
POLYGON_RPC_URL=https://rpc-mumbai.maticvigil.com
CHAIN_ID=80001

# Suas chaves (gere novas!)
PRIVATE_KEY_TESTNET=0x...
MINER_ADDRESS=0x...

# API Key (qualquer string por enquanto)
PRFI_API_KEY=test_api_key_123

# Configurações básicas
MAX_RETRIES=3
BATCH_SIZE=5
BLOCKS_DIRECTORY=./blocos
LOGS_DIRECTORY=./logs
EOF
```

### Gerar suas chaves

```python
# Execute este código para gerar suas chaves
from eth_account import Account

account = Account.create()
print(f"🔑 Seu endereço: {account.address}")
print(f"🔐 Sua chave privada: {account.privateKey.hex()}")
print(f"💡 Adicione estas informações no arquivo .env")
```

### Criar diretórios

```bash
mkdir blocos logs
```

## 💻 Passo 3: Primeira Requisição

### Código Python

```python
import asyncio
from prfi_core import PRFIClient

async def primeira_requisicao():
    # Criar cliente PRFI
    client = PRFIClient(
        api_key="test_api_key_123",
        miner_address="SEU_ENDERECO_AQUI",  # Do passo anterior
        private_key="SUA_CHAVE_PRIVADA_AQUI"  # Do passo anterior
    )
    
    # Fazer requisição com retry e fallback
    response = await client.request(
        url="https://httpbin.org/status/200",  # API de teste
        method="GET",
        fallback_url="https://httpbin.org/get",  # Fallback
        max_retries=3
    )
    
    print(f"✅ Status: {response.status_code}")
    print(f"🎯 Sucesso: {response.success}")
    print(f"🔄 Retries usados: {response.retries_used}")
    print(f"🔀 Fallback usado: {response.fallback_used}")
    print(f"💰 Pontos ganhos: {response.points_earned}")
    print(f"📦 Bloco minerado: {response.block_id}")
    
    return response

# Executar
if __name__ == "__main__":
    response = asyncio.run(primeira_requisicao())
```

### Executar o código

```bash
python primeira_requisicao.py
```

**Resultado esperado:**
```
✅ Status: 200
🎯 Sucesso: True
🔄 Retries usados: 0
🔀 Fallback usado: False
💰 Pontos ganhos: 0.4
📦 Bloco minerado: blk_abc123...
```

## ⛏️ Passo 4: Verificar Bloco Minerado

```bash
# Listar blocos minerados
prfi blocks list

# Ver detalhes do último bloco
prfi blocks show --latest

# Verificar assinatura digital
prfi blocks verify --block-id blk_abc123...
```

## 🔗 Passo 5: Submeter para Blockchain

```python
import asyncio
from submitter import BlockSubmitter, SubmissionConfig

async def submeter_blocos():
    # Configurar submitter
    config = SubmissionConfig(
        rpc_url="https://rpc-mumbai.maticvigil.com",
        contract_address="0x...",  # Endereço do contrato na testnet
        private_key="SUA_CHAVE_PRIVADA_AQUI",
        chain_id=80001,  # Mumbai testnet
        batch_size=5
    )
    
    submitter = BlockSubmitter(config)
    
    # Processar blocos pendentes
    results = await submitter.process_pending_blocks()
    
    for result in results:
        if result.success:
            print(f"✅ Batch submetido: {result.tx_hash}")
            print(f"📦 Blocos: {result.blocks_submitted}")
            print(f"💰 Pontos: {result.points_submitted}")
        else:
            print(f"❌ Erro: {result.error}")

# Executar
asyncio.run(submeter_blocos())
```

## 🎉 Passo 6: Verificar Tokens

```bash
# Verificar saldo na testnet
prfi balance --address SEU_ENDERECO --network mumbai

# Verificar transações
prfi transactions --address SEU_ENDERECO --network mumbai
```

## 📊 Exemplos Práticos

### Exemplo 1: E-commerce com Fallback

```python
async def processar_pagamento():
    client = PRFIClient(api_key="...", miner_address="0x...")
    
    response = await client.request(
        url="https://api.pagamento.com/processar",
        method="POST",
        data={
            "pedido_id": "12345",
            "valor": 99.90,
            "cartao": "****1234"
        },
        fallback_url="https://backup.pagamento.com/processar",
        max_retries=3,
        retry_delay=2.0
    )
    
    if response.success:
        print(f"💳 Pagamento processado!")
        print(f"💰 Tokens ganhos: {response.tokens_earned}")
    else:
        print(f"❌ Falha no pagamento: {response.error}")
```

### Exemplo 2: Webhook com Retry

```python
async def enviar_webhook():
    client = PRFIClient(api_key="...", miner_address="0x...")
    
    response = await client.request(
        url="https://cliente.com/webhook/pedido",
        method="POST",
        data={
            "event": "pedido.criado",
            "pedido_id": "12345",
            "timestamp": "2024-01-15T10:30:00Z"
        },
        headers={"X-Webhook-Secret": "secret123"},
        max_retries=5,
        exponential_backoff=True
    )
    
    print(f"📡 Webhook enviado: {response.success}")
    print(f"🔄 Tentativas: {response.retries_used + 1}")
```

### Exemplo 3: API com Rate Limiting

```python
async def consultar_api_limitada():
    client = PRFIClient(api_key="...", miner_address="0x...")
    
    # Fazer múltiplas requisições com retry automático
    for i in range(10):
        response = await client.request(
            url=f"https://api.exemplo.com/dados/{i}",
            method="GET",
            headers={"Authorization": "Bearer token123"},
            max_retries=3,
            retry_delay=1.0,
            exponential_backoff=True
        )
        
        if response.success:
            print(f"✅ Dados {i} obtidos - Pontos: {response.points_earned}")
        else:
            print(f"❌ Falha nos dados {i}: {response.error}")
        
        # Delay entre requisições
        await asyncio.sleep(0.5)
```

## 🔧 Comandos CLI Úteis

```bash
# Verificar configuração
prfi config validate

# Testar conexão
prfi test-connection

# Executar mineração de teste
prfi test-mining --events 10

# Monitorar blocos em tempo real
prfi blocks monitor

# Submeter blocos automaticamente
prfi submit --continuous --interval 300

# Verificar estatísticas
prfi stats

# Limpar blocos antigos
prfi cleanup --older-than 7d
```

## 📈 Monitoramento

### Métricas básicas

```python
from prfi_core import PRFIClient

# Habilitar métricas
client = PRFIClient(
    api_key="...",
    miner_address="0x...",
    enable_metrics=True
)

# Acessar métricas
print(f"Requisições totais: {client.metrics.total_requests}")
print(f"Sucessos: {client.metrics.successful_requests}")
print(f"Falhas: {client.metrics.failed_requests}")
print(f"Tokens ganhos: {client.metrics.total_tokens_earned}")
```

### Dashboard simples

```bash
# Iniciar servidor de métricas
prfi metrics-server --port 8080

# Acessar no navegador
# http://localhost:8080/metrics
```

## 🚨 Solução de Problemas

### Erro: "Conexão com blockchain falhou"
```bash
# Verificar RPC
curl -X POST -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' \
  https://rpc-mumbai.maticvigil.com

# Tentar RPC alternativo
export POLYGON_RPC_URL="https://matic-mumbai.chainstacklabs.com"
```

### Erro: "Chave privada inválida"
```python
# Verificar formato da chave
private_key = "0x..."  # Deve começar com 0x
assert len(private_key) == 66  # 64 caracteres + 0x
```

### Erro: "Diretório não encontrado"
```bash
# Criar diretórios necessários
mkdir -p blocos logs backups
chmod 755 blocos logs
```

## 🎯 Próximos Passos

Agora que você tem o básico funcionando:

1. **📚 Leia a documentação completa**: [README.md](../README.md)
2. **🔧 Configure para produção**: [INSTALLATION.md](INSTALLATION.md)
3. **🏗️ Entenda a arquitetura**: [ARCHITECTURE.md](ARCHITECTURE.md)
4. **💰 Aprenda sobre tokenização**: [TOKENIZATION.md](TOKENIZATION.md)
5. **🤝 Contribua para o projeto**: [CONTRIBUTING.md](../CONTRIBUTING.md)

## 💬 Precisa de Ajuda?

- **Discord**: [Comunidade PRFI](https://discord.gg/prfi)
- **GitHub**: [Issues](https://github.com/prfi-org/prfi-protocol/issues)
- **Email**: support@prfi.org

---

**🎉 Parabéns! Você está usando o PRFI Protocol!**

Agora suas integrações são mais robustas e você ganha tokens por cada evento entregue com sucesso. 🚀
