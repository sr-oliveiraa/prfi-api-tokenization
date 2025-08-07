# 🚀 PRFI CLI 2.0 - Interface Moderna para PRFI Protocol

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/prfi-protocol/prfi-cli)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Build](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/prfi-protocol/prfi-cli)

**Interface de linha de comando moderna e intuitiva para o PRFI Protocol** - transforme suas APIs em sistemas resilientes com retry automático, fallback inteligente e tokenização blockchain.

## ✨ Principais Funcionalidades

### 🎯 **Setup Intuitivo**
- **Wizard interativo** com perguntas simples
- **Templates pré-configurados** para diferentes casos de uso
- **Auto-configuração** de chaves criptográficas
- **Validação em tempo real** de configurações

### 🌐 **Dashboard Web Moderno**
- **Interface responsiva** construída com React + TypeScript
- **Monitoramento em tempo real** de APIs e métricas
- **Configuração visual** drag-and-drop
- **Logs interativos** com filtros avançados

### ⚡ **Performance Otimizada**
- **Retry inteligente** com backoff exponencial
- **Fallback automático** para endpoints alternativos
- **Batching otimizado** para blockchain
- **Cache inteligente** de respostas

### 🔐 **Segurança Avançada**
- **Assinatura digital** Ed25519
- **Validação criptográfica** de eventos
- **Rate limiting** configurável
- **HTTPS obrigatório** em produção

## 🚀 Instalação Rápida

```bash
# Instalar via pip
pip install prfi-cli

# Ou instalar a versão de desenvolvimento
git clone https://github.com/prfi-protocol/prfi-cli
cd prfi-cli
pip install -e .
```

## 🎯 Início Rápido

### 1. **Setup Inicial (30 segundos)**
```bash
# Setup interativo completo
prfi init

# Ou setup rápido com configurações padrão
prfi init --quick

# Ou usar template específico
prfi init --template ecommerce
```

### 2. **Testar Configuração**
```bash
# Testar todas as configurações
prfi test

# Testar APIs específicas
prfi test --apis payment-gateway inventory-api

# Testar conexão blockchain
prfi test --blockchain
```

### 3. **Deploy do Smart Contract**
```bash
# Deploy automático
prfi deploy

# Deploy em rede específica
prfi deploy --network bsc-mainnet

# Deploy com verificação
prfi deploy --verify
```

### 4. **Abrir Dashboard Web**
```bash
# Dashboard padrão (porta 8080)
prfi dashboard

# Dashboard com porta customizada
prfi dashboard --port 3000

# Dashboard público (acessível externamente)
prfi dashboard --public --open
```

## 📋 Templates Disponíveis

### 🛒 **E-commerce**
```bash
prfi init --template ecommerce
```
- Payment gateways (Stripe, PayPal)
- Inventory management
- Shipping APIs
- Configuração balanceada

### 💰 **Fintech**
```bash
prfi init --template fintech
```
- Banking APIs
- Credit checks
- Fraud detection
- Configuração agressiva (máxima resiliência)

### 🎮 **Gaming**
```bash
prfi init --template gaming
```
- Player stats
- Leaderboards
- Achievement systems
- Configuração de alta performance

### 🌐 **IoT**
```bash
prfi init --template iot
```
- Sensor data collection
- Device control
- Analytics APIs
- Configuração conservadora

### 📱 **Social Media**
```bash
prfi init --template social
```
- User management
- Content APIs
- Notification systems
- Configuração balanceada

## ⚙️ Comandos Principais

### 🎯 **Gerenciamento**
```bash
prfi status          # Status atual do sistema
prfi doctor          # Diagnosticar problemas
prfi config          # Gerenciar configurações
prfi monitor          # Monitoramento em tempo real
```

### 🧪 **Desenvolvimento**
```bash
prfi test            # Testar configuração
prfi test --watch    # Teste contínuo
prfi logs            # Ver logs em tempo real
prfi logs --follow   # Seguir logs
```

### 🚀 **Deploy e Produção**
```bash
prfi deploy          # Deploy do smart contract
prfi start           # Iniciar todos os serviços
prfi stop            # Parar todos os serviços
prfi restart         # Reiniciar serviços
```

### 📊 **Monitoramento**
```bash
prfi dashboard       # Interface web
prfi metrics         # Métricas detalhadas
prfi health          # Health check
prfi stats           # Estatísticas resumidas
```

## 🎨 Interface Web

### 📊 **Dashboard Principal**
- **Métricas em tempo real**: Requests, success rate, response time
- **Gráficos interativos**: Performance histórica das APIs
- **Status das APIs**: Monitoramento visual de saúde
- **Saldo de tokens**: PRFIC tokens ganhos

### 🌐 **Gerenciamento de APIs**
- **Lista visual** de todas as APIs configuradas
- **Teste individual** de cada endpoint
- **Configuração de fallbacks** drag-and-drop
- **Histórico de requests** com filtros

### ⛓️ **Blockchain**
- **Status do contrato** PRFIC
- **Transações recentes** com links para explorer
- **Saldo de tokens** em tempo real
- **Deploy e verificação** de contratos

### 📝 **Logs Interativos**
- **Filtros avançados** por nível, API, timestamp
- **Busca em tempo real** nos logs
- **Export** de logs em diferentes formatos
- **Alertas automáticos** para erros críticos

## 🔧 Configuração Avançada

### 📁 **Estrutura de Arquivos**
```
meu-projeto-prfi/
├── prfi.config.yaml      # Configuração principal
├── .env                  # Variáveis de ambiente
├── logs/                 # Logs do sistema
├── data/                 # Dados locais
└── contracts/            # Smart contracts deployados
```

### ⚙️ **Arquivo de Configuração**
```yaml
# prfi.config.yaml
project:
  name: "meu-projeto-prfi"
  version: "1.0.0"

prfi:
  retry:
    max_attempts: 5
    initial_delay: 1.0
    max_delay: 300.0
  
  fallback:
    enabled: true
    auto_discover: true
  
  tokenization:
    enabled: true
    min_difficulty: 4

blockchain:
  network: "bsc-testnet"
  auto_deploy: true

apis:
  - name: "Payment API"
    url: "https://api.stripe.com/v1/charges"
    method: "POST"
    fallback_url: "https://api.paypal.com/v1/payments"
    timeout: 30

monitoring:
  enabled: true
  dashboard_port: 8080
  metrics_enabled: true
```

### 🌍 **Variáveis de Ambiente**
```bash
# .env
PRFI_PRIVATE_KEY=0x...
PRFI_CONTRACT_ADDRESS=0x...
PRFI_RPC_URL=https://bsc-dataseed1.binance.org
PRFI_LOG_LEVEL=INFO
```

## 🔗 Integrações

### 📦 **Como Biblioteca Python**
```python
from prfi_cli import PRFIClient

# Criar cliente
client = PRFIClient.from_config("prfi.config.yaml")

# Fazer request com retry/fallback automático
response = await client.request(
    url="https://api.exemplo.com/endpoint",
    method="POST",
    data={"key": "value"},
    fallback_url="https://backup.exemplo.com/endpoint"
)

print(f"Status: {response.status_code}")
print(f"Tokens ganhos: {response.tokens_earned}")
```

### 🌐 **API REST**
```bash
# Iniciar servidor API
prfi server --port 8000

# Fazer requests via HTTP
curl -X POST http://localhost:8000/api/request \
  -H "Content-Type: application/json" \
  -d '{"url": "https://api.exemplo.com", "method": "GET"}'
```

### 🐳 **Docker**
```dockerfile
FROM python:3.11-slim

RUN pip install prfi-cli

COPY prfi.config.yaml /app/
WORKDIR /app

CMD ["prfi", "start"]
```

## 📈 Monitoramento e Métricas

### 📊 **Métricas Disponíveis**
- **Total de requests** processados
- **Taxa de sucesso** (%)
- **Tempo médio de resposta** (ms)
- **Tokens PRFIC** ganhos
- **APIs ativas** vs inativas
- **Requests com fallback** (%)

### 🚨 **Alertas Automáticos**
- **Taxa de erro** acima do limite
- **Tempo de resposta** muito alto
- **API indisponível** por muito tempo
- **Saldo de gas** baixo na blockchain

### 📈 **Dashboards Grafana**
```bash
# Exportar métricas para Prometheus
prfi config set monitoring.prometheus.enabled true
prfi config set monitoring.prometheus.port 9090

# Importar dashboard Grafana pré-configurado
prfi dashboard --export-grafana > prfi-dashboard.json
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Veja nosso [guia de contribuição](CONTRIBUTING.md).

### 🛠️ **Desenvolvimento Local**
```bash
# Clonar repositório
git clone https://github.com/prfi-protocol/prfi-cli
cd prfi-cli

# Instalar dependências de desenvolvimento
pip install -e ".[dev]"

# Executar testes
pytest

# Executar linting
black . && flake8 .

# Executar servidor de desenvolvimento
prfi dashboard --dev
```

## 📚 Documentação

- 📖 **[Documentação Completa](https://docs.prfi.protocol)**
- 🎯 **[Guia de Início Rápido](https://docs.prfi.protocol/quickstart)**
- 🔧 **[Referência da API](https://docs.prfi.protocol/api)**
- 💡 **[Exemplos](https://github.com/prfi-protocol/examples)**

## 🆘 Suporte

- 💬 **[Discord](https://discord.gg/prfi-protocol)**
- 🐛 **[Issues](https://github.com/prfi-protocol/prfi-cli/issues)**
- 📧 **[Email](mailto:support@prfi.protocol)**
- 📚 **[FAQ](https://docs.prfi.protocol/faq)**

## 📄 Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).

---

<div align="center">

**🚀 Transforme suas APIs em sistemas resilientes com PRFI Protocol!**

[Website](https://prfi.protocol) • [Documentação](https://docs.prfi.protocol) • [Discord](https://discord.gg/prfi-protocol) • [Twitter](https://twitter.com/prfi_protocol)

</div>
