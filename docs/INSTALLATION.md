# 📦 Installation Guide - PRFI Protocol

Complete guide to install and configure PRFI Protocol for tokenizing your APIs.

## 📋 Prerequisites

### System Requirements
- **Node.js**: 16.0.0 or higher
- **npm**: 8.0.0 or higher
- **Git**: Latest version
- **Operating System**: Windows 10+, macOS 11+, Ubuntu 20.04+

### Blockchain Requirements
- **Wallet**: MetaMask or similar (with private key access)
- **BNB**: For gas fees on BSC Mainnet
- **Test BNB**: For testing on BSC Testnet (free from faucet)

### Hardware Requirements
- **RAM**: Minimum 4GB, recommended 8GB+
- **Storage**: Minimum 5GB free space
- **Network**: Stable internet connection

## 🚀 Instalação Rápida

### Via pip (Recomendado)

```bash
# Instalar versão estável
pip install prfi-protocol

# Verificar instalação
prfi --version
```

### Via código fonte

```bash
# Clonar repositório
git clone https://github.com/prfi-org/prfi-protocol.git
cd prfi-protocol

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Instalar em modo desenvolvimento
pip install -e .
```

## 🔧 Configuração Inicial

### 1. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar configurações
nano .env  # ou seu editor preferido
```

### 2. Configurações Obrigatórias

```env
# Blockchain (escolha uma rede)
POLYGON_RPC_URL=https://polygon-rpc.com
MUMBAI_RPC_URL=https://rpc-mumbai.maticvigil.com

# Chaves (GERE SUAS PRÓPRIAS CHAVES)
PRIVATE_KEY_MAINNET=0x...
MINER_ADDRESS=0x...

# API Key PRFI
PRFI_API_KEY=your_api_key_here
```

### 3. Criar Diretórios

```bash
# Criar estrutura de diretórios
mkdir -p blocos logs backups

# Definir permissões (Linux/macOS)
chmod 755 blocos logs
chmod 700 backups
```

### 4. Testar Instalação

```bash
# Testar conexão com blockchain
prfi test-connection

# Verificar configuração
prfi config validate

# Executar teste básico
prfi test-mining
```

## 🏗️ Instalação por Ambiente

### Desenvolvimento Local

```bash
# Instalar com dependências de desenvolvimento
pip install -e ".[dev]"

# Configurar para testnet
export ENVIRONMENT=development
export POLYGON_RPC_URL=$MUMBAI_RPC_URL
export PRFIC_CONTRACT_ADDRESS=$PRFIC_CONTRACT_TESTNET

# Executar testes
pytest
```

### Staging/Homologação

```bash
# Instalar versão específica
pip install prfi-protocol==1.0.0

# Configurar para testnet com dados de produção
export ENVIRONMENT=staging
export POLYGON_RPC_URL=$MUMBAI_RPC_URL
export LOG_LEVEL=INFO
export BATCH_SIZE=5

# Configurar monitoramento
export ENABLE_METRICS=true
export METRICS_PORT=8080
```

### Produção

```bash
# Instalar versão estável
pip install prfi-protocol

# Configurar para mainnet
export ENVIRONMENT=production
export POLYGON_RPC_URL=$POLYGON_RPC_URL
export LOG_LEVEL=WARNING
export BATCH_SIZE=20

# Configurar alta disponibilidade
export CONFIRMATION_BLOCKS=12
export MAX_RETRIES=5
export ENABLE_RATE_LIMITING=true
```

## 🐳 Instalação com Docker

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos
COPY requirements.txt .
COPY . .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e .

# Criar diretórios
RUN mkdir -p blocos logs

# Configurar usuário não-root
RUN useradd -m -u 1000 prfi
RUN chown -R prfi:prfi /app
USER prfi

# Expor porta para métricas
EXPOSE 8080

# Comando padrão
CMD ["prfi", "start", "--continuous"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  prfi-protocol:
    build: .
    environment:
      - ENVIRONMENT=production
      - POLYGON_RPC_URL=${POLYGON_RPC_URL}
      - PRIVATE_KEY_MAINNET=${PRIVATE_KEY_MAINNET}
      - MINER_ADDRESS=${MINER_ADDRESS}
      - PRFI_API_KEY=${PRFI_API_KEY}
    volumes:
      - ./blocos:/app/blocos
      - ./logs:/app/logs
    ports:
      - "8080:8080"
    restart: unless-stopped
    
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

### Executar com Docker

```bash
# Construir imagem
docker build -t prfi-protocol .

# Executar container
docker run -d \
  --name prfi \
  -e POLYGON_RPC_URL="https://polygon-rpc.com" \
  -e PRIVATE_KEY_MAINNET="0x..." \
  -e MINER_ADDRESS="0x..." \
  -v $(pwd)/blocos:/app/blocos \
  -v $(pwd)/logs:/app/logs \
  -p 8080:8080 \
  prfi-protocol

# Ou usar docker-compose
docker-compose up -d
```

## ☸️ Instalação no Kubernetes

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prfi-protocol
spec:
  replicas: 3
  selector:
    matchLabels:
      app: prfi-protocol
  template:
    metadata:
      labels:
        app: prfi-protocol
    spec:
      containers:
      - name: prfi-protocol
        image: prfi-protocol:latest
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: POLYGON_RPC_URL
          valueFrom:
            secretKeyRef:
              name: prfi-secrets
              key: polygon-rpc-url
        - name: PRIVATE_KEY_MAINNET
          valueFrom:
            secretKeyRef:
              name: prfi-secrets
              key: private-key
        volumeMounts:
        - name: blocks-storage
          mountPath: /app/blocos
        - name: logs-storage
          mountPath: /app/logs
        ports:
        - containerPort: 8080
          name: metrics
      volumes:
      - name: blocks-storage
        persistentVolumeClaim:
          claimName: prfi-blocks-pvc
      - name: logs-storage
        persistentVolumeClaim:
          claimName: prfi-logs-pvc
```

### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: prfi-protocol-service
spec:
  selector:
    app: prfi-protocol
  ports:
  - port: 8080
    targetPort: 8080
    name: metrics
  type: ClusterIP
```

## 🔐 Configuração de Segurança

### Gerar Chaves Privadas

```bash
# Usando Python
python -c "
from eth_account import Account
account = Account.create()
print(f'Address: {account.address}')
print(f'Private Key: {account.privateKey.hex()}')
"

# Ou usando Node.js
node -e "
const { Wallet } = require('ethers');
const wallet = Wallet.createRandom();
console.log('Address:', wallet.address);
console.log('Private Key:', wallet.privateKey);
"
```

### Configurar Permissões

```bash
# Proteger arquivo .env
chmod 600 .env

# Proteger diretório de logs
chmod 700 logs

# Configurar firewall (Ubuntu)
sudo ufw allow 8080/tcp  # Métricas
sudo ufw enable
```

## 📊 Verificação da Instalação

### Testes Básicos

```bash
# Verificar versão
prfi --version

# Testar configuração
prfi config validate

# Testar conexão blockchain
prfi test-connection

# Executar mineração de teste
prfi test-mining --events 5

# Verificar métricas
curl http://localhost:8080/metrics
```

### Testes Avançados

```bash
# Executar suite completa de testes
pytest tests/

# Teste de stress
python tests/test_stress_scenarios.py

# Teste de integração blockchain
python tests/test_blockchain_integration.py
```

## 🚨 Solução de Problemas

### Problemas Comuns

#### Erro de Conexão Blockchain
```bash
# Verificar RPC URL
curl -X POST -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' \
  $POLYGON_RPC_URL

# Testar com RPC alternativo
export POLYGON_RPC_URL="https://rpc-mainnet.matic.network"
```

#### Erro de Permissões
```bash
# Verificar permissões de diretórios
ls -la blocos logs

# Corrigir permissões
chmod 755 blocos logs
chown $USER:$USER blocos logs
```

#### Erro de Dependências
```bash
# Reinstalar dependências
pip uninstall prfi-protocol
pip install --upgrade pip
pip install prfi-protocol

# Ou limpar cache
pip cache purge
pip install --no-cache-dir prfi-protocol
```

### Logs de Debug

```bash
# Habilitar debug
export LOG_LEVEL=DEBUG
export DEBUG=true

# Executar com logs detalhados
prfi start --verbose

# Verificar logs
tail -f logs/prfi.log
```

## 📞 Suporte

Se você encontrar problemas durante a instalação:

1. **Verifique os logs**: `tail -f logs/prfi.log`
2. **Consulte a documentação**: [docs/](../docs/)
3. **Abra uma issue**: [GitHub Issues](https://github.com/prfi-org/prfi-protocol/issues)
4. **Entre no Discord**: [Comunidade PRFI](https://discord.gg/prfi)

---

**Próximo passo**: [Configuração](CONFIGURATION.md)
