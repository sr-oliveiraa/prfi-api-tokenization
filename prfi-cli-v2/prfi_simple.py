#!/usr/bin/env python3
"""
PRFI CLI 2.0 - Versão Simplificada para Windows
Sem emojis, compatível com qualquer terminal
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def main():
    """CLI simplificado sem emojis"""
    
    print("=" * 60)
    print("PRFI CLI 2.0 - Interface Simplificada")
    print("=" * 60)
    print()
    
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1]
    
    if command == "init":
        handle_init()
    elif command == "test":
        handle_test()
    elif command == "dashboard":
        handle_dashboard()
    elif command == "deploy":
        handle_deploy()
    elif command == "help" or command == "--help":
        show_help()
    else:
        print(f"Comando desconhecido: {command}")
        show_help()

def show_help():
    """Mostrar ajuda"""
    print("Comandos disponíveis:")
    print()
    print("  init        - Setup inicial do projeto")
    print("  test        - Executar testes")
    print("  dashboard   - Abrir dashboard web")
    print("  deploy      - Deploy de smart contract")
    print("  help        - Mostrar esta ajuda")
    print()
    print("Exemplos:")
    print("  python prfi_simple.py init")
    print("  python prfi_simple.py test")
    print("  python prfi_simple.py dashboard")

def handle_init():
    """Setup inicial"""
    print("[INIT] Iniciando setup do PRFI Protocol...")
    print()
    
    # Configuração básica
    config = {
        "project": {
            "name": "meu-projeto-prfi",
            "description": "Projeto PRFI gerado automaticamente",
            "version": "1.0.0"
        },
        "prfi": {
            "retry": {
                "max_attempts": 5,
                "initial_delay": 1.0,
                "max_delay": 300.0,
                "multiplier": 2.0,
                "jitter": True
            },
            "fallback": {
                "enabled": True,
                "auto_discover": True
            },
            "tokenization": {
                "enabled": True,
                "min_difficulty": 4
            }
        },
        "blockchain": {
            "network": "bsc-testnet",
            "auto_deploy": True
        },
        "apis": [],
        "monitoring": {
            "enabled": True,
            "dashboard_port": 8080
        }
    }
    
    # Salvar configuração
    import yaml
    config_file = Path("prfi.config.yaml")
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, indent=2)
        
        print(f"[OK] Configuracao salva em: {config_file}")
        print()
        print("Proximos passos:")
        print("1. python prfi_simple.py test")
        print("2. python prfi_simple.py dashboard")
        print("3. python prfi_simple.py deploy")
        
    except Exception as e:
        print(f"[ERRO] Falha ao salvar configuracao: {e}")

def handle_test():
    """Executar testes"""
    print("[TEST] Executando testes do PRFI Protocol...")
    print()
    
    # Verificar configuração
    config_file = Path("prfi.config.yaml")
    if not config_file.exists():
        print("[ERRO] Arquivo de configuracao nao encontrado")
        print("Execute: python prfi_simple.py init")
        return
    
    print("[OK] Arquivo de configuracao encontrado")
    
    # Testar importação do PRFI Core
    prfi_core_path = Path("../prfi-core")
    if prfi_core_path.exists():
        print("[OK] PRFI Core encontrado")
        
        # Tentar importar módulos
        sys.path.insert(0, str(prfi_core_path))
        try:
            from modelos import PRFIEvent, EventStatus
            print("[OK] Modelos PRFI importados")
        except ImportError as e:
            print(f"[AVISO] Erro ao importar modelos: {e}")
        
        try:
            import cliente_descentralizado
            print("[OK] Cliente descentralizado importado")
        except ImportError as e:
            print(f"[AVISO] Erro ao importar cliente: {e}")
    else:
        print("[AVISO] PRFI Core nao encontrado")
    
    # Testar conexão blockchain
    try:
        from web3 import Web3
        from web3.middleware import geth_poa_middleware
        
        rpc_url = "https://data-seed-prebsc-1-s1.binance.org:8545"
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        if w3.is_connected():
            latest_block = w3.eth.get_block('latest')
            print(f"[OK] Conectado a BSC Testnet - Bloco: {latest_block.number}")
        else:
            print("[ERRO] Nao foi possivel conectar a blockchain")
            
    except ImportError:
        print("[AVISO] web3 nao instalado - execute: pip install web3")
    except Exception as e:
        print(f"[ERRO] Erro na blockchain: {e}")
    
    print()
    print("[CONCLUIDO] Testes executados")

def handle_dashboard():
    """Iniciar dashboard"""
    print("[DASHBOARD] Iniciando dashboard web...")
    print()
    
    try:
        # Verificar se FastAPI está instalado
        import uvicorn
        from fastapi import FastAPI
        
        print("[OK] FastAPI encontrado")
        print("[INFO] Iniciando servidor em http://localhost:8080")
        print("[INFO] Pressione Ctrl+C para parar")
        print()
        
        # Criar app básica
        app = FastAPI(title="PRFI Dashboard")
        
        @app.get("/")
        async def root():
            return {
                "message": "PRFI Dashboard funcionando!",
                "version": "2.0.0",
                "status": "online"
            }
        
        @app.get("/api/status")
        async def status():
            return {
                "status": "online",
                "timestamp": time.time()
            }
        
        # Iniciar servidor
        uvicorn.run(app, host="127.0.0.1", port=8080, log_level="info")
        
    except ImportError:
        print("[ERRO] FastAPI nao instalado")
        print("Execute: pip install fastapi uvicorn")
    except Exception as e:
        print(f"[ERRO] Falha ao iniciar dashboard: {e}")

def handle_deploy():
    """Deploy de contrato"""
    print("[DEPLOY] Simulando deploy de smart contract...")
    print()
    
    # Verificar ambiente
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] Node.js encontrado: {result.stdout.strip()}")
        else:
            print("[ERRO] Node.js nao encontrado")
            return
    except FileNotFoundError:
        print("[ERRO] Node.js nao instalado")
        return
    
    # Verificar Hardhat
    try:
        result = subprocess.run(["npx", "hardhat", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("[OK] Hardhat encontrado")
        else:
            print("[AVISO] Hardhat nao encontrado")
    except:
        print("[AVISO] Erro ao verificar Hardhat")
    
    print()
    print("[SIMULACAO] Deploy seria executado com:")
    print("- Rede: bsc-testnet")
    print("- Contrato: PRFIC")
    print("- Gas estimado: 2,500,000")
    print()
    print("[INFO] Para deploy real, configure .env e execute:")
    print("npx hardhat run scripts/deploy.js --network bscTestnet")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Operacao cancelada pelo usuario")
    except Exception as e:
        print(f"\n[ERRO] Erro inesperado: {e}")
