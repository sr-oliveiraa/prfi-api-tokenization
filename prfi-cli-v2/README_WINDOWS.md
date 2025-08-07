# 🚀 PRFI CLI 2.0 - Guia para Windows

**Interface moderna e simplificada para PRFI Protocol, compatível com Windows**

## ⚡ Início Rápido (30 segundos)

### 1. **Setup Inicial**
```cmd
python prfi_simple.py init
```

### 2. **Executar Testes**
```cmd
python prfi_simple.py test
```

### 3. **Abrir Dashboard**
```cmd
python prfi_simple.py dashboard
```

### 4. **Simular Deploy**
```cmd
python prfi_simple.py deploy
```

## 📋 Comandos Disponíveis

### `init` - Setup Inicial
```cmd
python prfi_simple.py init
```
- Cria arquivo `prfi.config.yaml`
- Configuração padrão otimizada
- Pronto para usar em 30 segundos

### `test` - Executar Testes
```cmd
python prfi_simple.py test
```
- Testa configuração
- Verifica integração PRFI-Core
- Testa conexão blockchain
- Valida ambiente

### `dashboard` - Interface Web
```cmd
python prfi_simple.py dashboard
```
- Inicia servidor web local
- Interface em http://localhost:8080
- APIs REST funcionais
- Monitoramento em tempo real

### `deploy` - Deploy de Contrato
```cmd
python prfi_simple.py deploy
```
- Simula deploy de smart contract
- Verifica ambiente (Node.js, Hardhat)
- Mostra configurações necessárias

## 🔧 Solução de Problemas

### **Problema: Emojis não aparecem**
✅ **Solução**: Use `prfi_simple.py` (sem emojis)

### **Problema: Encoding error**
✅ **Solução**: 
```cmd
chcp 65001
python prfi_simple.py init
```

### **Problema: web3 não instalado**
✅ **Solução**:
```cmd
pip install web3
```

### **Problema: FastAPI não instalado**
✅ **Solução**:
```cmd
pip install fastapi uvicorn
```

## 📊 O que cada comando faz

### **Init (Setup)**
```
[INIT] Iniciando setup do PRFI Protocol...
[OK] Configuracao salva em: prfi.config.yaml

Proximos passos:
1. python prfi_simple.py test
2. python prfi_simple.py dashboard
3. python prfi_simple.py deploy
```

### **Test (Testes)**
```
[TEST] Executando testes do PRFI Protocol...
[OK] Arquivo de configuracao encontrado
[OK] PRFI Core encontrado
[OK] Modelos PRFI importados
[OK] Conectado a BSC Testnet - Bloco: 34567890
[CONCLUIDO] Testes executados
```

### **Dashboard (Interface Web)**
```
[DASHBOARD] Iniciando dashboard web...
[OK] FastAPI encontrado
[INFO] Iniciando servidor em http://localhost:8080
[INFO] Pressione Ctrl+C para parar
```

### **Deploy (Smart Contract)**
```
[DEPLOY] Simulando deploy de smart contract...
[OK] Node.js encontrado: v18.17.0
[OK] Hardhat encontrado
[SIMULACAO] Deploy seria executado com:
- Rede: bsc-testnet
- Contrato: PRFIC
- Gas estimado: 2,500,000
```

## 🎯 Funcionalidades Implementadas

### ✅ **CLI Simplificado**
- Interface sem emojis (compatível Windows)
- Comandos intuitivos
- Output claro e informativo
- Tratamento de erros

### ✅ **Integração PRFI-Core**
- Importação de modelos
- Validação de configuração
- Testes automáticos
- Detecção de problemas

### ✅ **Testes Reais**
- Configuração
- PRFI Core
- Blockchain (BSC Testnet)
- Ambiente de desenvolvimento

### ✅ **Dashboard Web**
- Servidor FastAPI
- APIs REST
- Interface web básica
- Monitoramento

### ✅ **Deploy Simulation**
- Verificação de ambiente
- Validação de dependências
- Simulação de deploy
- Instruções claras

## 🚀 Próximos Passos

Após executar os comandos básicos:

1. **Configure suas APIs** no arquivo `prfi.config.yaml`
2. **Instale dependências** para blockchain: `pip install web3`
3. **Configure Node.js** para deploy real
4. **Explore o dashboard** em http://localhost:8080

## 💡 Dicas

### **Para melhor experiência:**
- Use Windows Terminal ou PowerShell
- Configure encoding UTF-8: `chcp 65001`
- Instale todas as dependências: `pip install -r requirements.txt`

### **Para desenvolvimento:**
- Use `prfi.py` (versão completa com emojis)
- Configure IDE com UTF-8
- Use terminal com suporte Unicode

## 🆘 Suporte

Se encontrar problemas:

1. **Verifique encoding**: `chcp 65001`
2. **Use versão simples**: `python prfi_simple.py`
3. **Instale dependências**: `pip install web3 fastapi uvicorn`
4. **Verifique Python**: `python --version` (3.8+)

---

**🎉 PRFI CLI 2.0 - Transformando APIs em sistemas resilientes!**
