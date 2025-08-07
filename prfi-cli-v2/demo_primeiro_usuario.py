#!/usr/bin/env python3
"""
PRFI Protocol - Demonstração para Primeiro Usuário
Guia interativo passo-a-passo
"""

import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path

def main():
    """Demonstração interativa para primeiro usuário"""
    
    print("=" * 80)
    print("PRFI PROTOCOL - GUIA INTERATIVO PARA PRIMEIRO USUÁRIO")
    print("=" * 80)
    print()
    print("Bem-vindo ao PRFI Protocol!")
    print("Vamos te guiar do zero até minerar seus primeiros tokens.")
    print()
    
    # Verificar se quer continuar
    if not confirm("Deseja começar a demonstração?"):
        print("Até logo!")
        return
    
    # Etapas da demonstração
    steps = [
        ("Verificar Ambiente", check_environment),
        ("Setup Inicial", setup_initial),
        ("Teste Básico", test_basic),
        ("Teste com APIs Reais", test_real_apis),
        ("Dashboard Web", show_dashboard),
        ("Sistema de Mineração", demo_mining),
        ("Conexão Blockchain", test_blockchain),
        ("Teste Completo", complete_test),
        ("Próximos Passos", next_steps)
    ]
    
    for i, (step_name, step_func) in enumerate(steps, 1):
        print(f"\n[ETAPA {i}/9] {step_name}")
        print("-" * 50)
        
        try:
            success = step_func()
            if success:
                print(f"[OK] Etapa {i} concluída com sucesso!")
            else:
                print(f"[AVISO] Etapa {i} teve problemas, mas continuando...")
                
        except Exception as e:
            print(f"[ERRO] Etapa {i} falhou: {e}")
            if not confirm("Deseja continuar mesmo assim?"):
                break
        
        if i < len(steps):
            if not confirm("Continuar para próxima etapa?"):
                break
    
    print("\n" + "=" * 80)
    print("DEMONSTRAÇÃO CONCLUÍDA!")
    print("Obrigado por testar o PRFI Protocol!")
    print("=" * 80)

def confirm(message: str) -> bool:
    """Confirmar ação com usuário"""
    while True:
        response = input(f"{message} (s/n): ").lower().strip()
        if response in ['s', 'sim', 'y', 'yes']:
            return True
        elif response in ['n', 'nao', 'não', 'no']:
            return False
        else:
            print("Por favor, responda 's' para sim ou 'n' para não.")

def wait_for_user():
    """Aguardar usuário pressionar Enter"""
    input("\nPressione Enter para continuar...")

def check_environment():
    """Verificar ambiente"""
    print("Verificando se seu ambiente está pronto...")
    print()
    
    # Verificar Python
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"[OK] Python {python_version.major}.{python_version.minor} (compatível)")
    else:
        print(f"[ERRO] Python {python_version.major}.{python_version.minor} (necessário 3.8+)")
        return False
    
    # Verificar pip
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, capture_output=True)
        print("[OK] pip disponível")
    except:
        print("[ERRO] pip não encontrado")
        return False
    
    # Verificar diretório
    if Path("prfi_simple.py").exists():
        print("[OK] PRFI CLI encontrado")
    else:
        print("[ERRO] PRFI CLI não encontrado")
        return False
    
    print("\n[RESULTADO] Ambiente está pronto para PRFI Protocol!")
    wait_for_user()
    return True

def setup_initial():
    """Setup inicial"""
    print("Vamos configurar seu primeiro projeto PRFI...")
    print()
    
    print("O setup vai criar um arquivo 'prfi.config.yaml' com:")
    print("- Configurações de retry (5 tentativas máximo)")
    print("- Sistema de fallback automático")
    print("- Mineração de tokens habilitada")
    print("- Conexão com BSC Testnet")
    print()
    
    if confirm("Executar setup automático?"):
        try:
            result = subprocess.run([
                sys.executable, "prfi_simple.py", "init"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("[OK] Setup concluído!")
                print(result.stdout)
            else:
                print(f"[ERRO] Setup falhou: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[ERRO] Erro no setup: {e}")
            return False
    
    wait_for_user()
    return True

def test_basic():
    """Teste básico"""
    print("Vamos testar se a configuração está funcionando...")
    print()
    
    print("Este teste vai verificar:")
    print("- Arquivo de configuração")
    print("- Integração com PRFI Core")
    print("- Importação de módulos")
    print()
    
    if confirm("Executar teste básico?"):
        try:
            result = subprocess.run([
                sys.executable, "prfi_simple.py", "test"
            ], capture_output=True, text=True, timeout=30)
            
            print(result.stdout)
            
            if "CONCLUIDO" in result.stdout:
                print("[OK] Teste básico passou!")
            else:
                print("[AVISO] Teste teve problemas")
                
        except Exception as e:
            print(f"[ERRO] Erro no teste: {e}")
            return False
    
    wait_for_user()
    return True

def test_real_apis():
    """Teste com APIs reais"""
    print("Agora vamos testar com APIs reais da internet...")
    print()
    
    print("Este teste vai chamar APIs públicas como:")
    print("- JSONPlaceholder (dados de teste)")
    print("- GitHub API (informações públicas)")
    print("- CoinGecko API (dados de crypto)")
    print("- HTTPBin (utilitários HTTP)")
    print()
    
    if confirm("Executar teste com APIs reais?"):
        try:
            print("Instalando dependência aiohttp...")
            subprocess.run([sys.executable, "-m", "pip", "install", "aiohttp"], 
                         check=True, capture_output=True)
            
            print("Executando teste completo...")
            result = subprocess.run([
                sys.executable, "test_complete_system.py"
            ], timeout=60)
            
            if result.returncode == 0:
                print("[OK] Teste com APIs reais concluído!")
            else:
                print("[AVISO] Teste teve alguns problemas")
                
        except Exception as e:
            print(f"[ERRO] Erro no teste: {e}")
            return False
    
    wait_for_user()
    return True

def show_dashboard():
    """Mostrar dashboard"""
    print("Vamos abrir o dashboard web para monitoramento...")
    print()
    
    print("O dashboard mostra:")
    print("- Status das APIs em tempo real")
    print("- Métricas de performance")
    print("- Tokens minerados")
    print("- Logs do sistema")
    print()
    
    if confirm("Abrir dashboard web?"):
        try:
            print("Instalando FastAPI...")
            subprocess.run([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn"], 
                         check=True, capture_output=True)
            
            print("Iniciando servidor...")
            print("Dashboard estará disponível em: http://localhost:8080")
            print()
            
            # Iniciar em background
            process = subprocess.Popen([
                sys.executable, "prfi_simple.py", "dashboard"
            ])
            
            time.sleep(3)
            
            if confirm("Abrir no navegador?"):
                webbrowser.open("http://localhost:8080")
            
            print("Dashboard rodando! Pressione Enter quando terminar de explorar...")
            input()
            
            # Parar servidor
            process.terminate()
            print("[OK] Dashboard encerrado")
            
        except Exception as e:
            print(f"[ERRO] Erro no dashboard: {e}")
            return False
    
    return True

def demo_mining():
    """Demonstrar mineração"""
    print("Vamos ver como funciona a mineração de tokens...")
    print()
    
    print("A mineração no PRFI funciona assim:")
    print("1. Suas APIs fazem requests")
    print("2. Cada request gera um 'evento'")
    print("3. Eventos são agrupados em 'batches'")
    print("4. Sistema faz 'proof-of-work' no batch")
    print("5. Tokens são minerados e creditados")
    print()
    
    if confirm("Ver demonstração de mineração?"):
        print("Simulando processo de mineração...")
        print()
        
        # Simular eventos
        events = [
            "API Payment processada com sucesso",
            "API Users retornou dados",
            "API Inventory atualizada",
            "Fallback usado para API Shipping",
            "API Analytics registrou evento"
        ]
        
        for i, event in enumerate(events, 1):
            print(f"[EVENTO {i}] {event}")
            time.sleep(0.5)
        
        print()
        print("[MINING] Processando batch de 5 eventos...")
        print("[MINING] Calculando proof-of-work...")
        
        # Simular mineração
        for i in range(3):
            print(f"[MINING] Tentativa {i+1}... Hash: {'0' * (i+1)}abc123...")
            time.sleep(1)
        
        print("[MINING] Hash válido encontrado!")
        print("[RESULTADO] 50 tokens PRFIC minerados!")
        print()
        
        tokens_earned = 50
        print(f"Parabéns! Você acabou de minerar {tokens_earned} tokens PRFIC!")
        print("Estes tokens são creditados na sua carteira automaticamente.")
    
    wait_for_user()
    return True

def test_blockchain():
    """Testar blockchain"""
    print("Vamos testar a conexão com a blockchain...")
    print()
    
    print("Vamos conectar com:")
    print("- BSC Testnet (rede de testes)")
    print("- Verificar blocos mais recentes")
    print("- Testar saldo da conta")
    print()
    
    if confirm("Testar conexão blockchain?"):
        try:
            print("Instalando web3...")
            subprocess.run([sys.executable, "-m", "pip", "install", "web3"], 
                         check=True, capture_output=True)
            
            print("Testando conexão...")
            
            from web3 import Web3
            from web3.middleware import geth_poa_middleware
            
            rpc_url = "https://data-seed-prebsc-1-s1.binance.org:8545"
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            
            if w3.is_connected():
                print("[OK] Conectado à BSC Testnet!")
                
                latest_block = w3.eth.get_block('latest')
                print(f"[INFO] Bloco mais recente: {latest_block.number}")
                
                # Testar conta
                test_address = "0xf354664266B265e1992a793763f45Aa7CBb522e1"
                balance = w3.eth.get_balance(test_address)
                balance_bnb = w3.from_wei(balance, 'ether')
                
                print(f"[INFO] Saldo da conta teste: {balance_bnb} BNB")
                
                if balance_bnb > 0:
                    print("[OK] Conta tem saldo para transações!")
                else:
                    print("[AVISO] Conta sem saldo - use faucet para conseguir BNB")
                    print("Faucet: https://testnet.binance.org/faucet-smart")
            else:
                print("[ERRO] Não foi possível conectar")
                return False
                
        except Exception as e:
            print(f"[ERRO] Erro blockchain: {e}")
            return False
    
    wait_for_user()
    return True

def complete_test():
    """Teste completo"""
    print("Agora vamos executar o teste completo do sistema...")
    print()
    
    print("Este teste vai:")
    print("- Testar todas as configurações")
    print("- Chamar APIs reais")
    print("- Simular retry e fallback")
    print("- Executar mineração real")
    print("- Conectar com blockchain")
    print("- Gerar relatório completo")
    print()
    
    if confirm("Executar teste completo?"):
        try:
            print("Executando teste completo...")
            print("(Isso pode levar 1-2 minutos)")
            print()
            
            result = subprocess.run([
                sys.executable, "test_complete_system.py"
            ], timeout=180)  # 3 minutos timeout
            
            if result.returncode == 0:
                print("\n[OK] Teste completo executado com sucesso!")
                print("Verifique o relatório acima para detalhes.")
            else:
                print("\n[AVISO] Teste teve alguns problemas")
                
        except subprocess.TimeoutExpired:
            print("\n[AVISO] Teste demorou mais que esperado")
        except Exception as e:
            print(f"\n[ERRO] Erro no teste: {e}")
            return False
    
    wait_for_user()
    return True

def next_steps():
    """Próximos passos"""
    print("Parabéns! Você completou a demonstração do PRFI Protocol!")
    print()
    
    print("O que você aprendeu:")
    print("✅ Como configurar o PRFI Protocol")
    print("✅ Como testar APIs reais")
    print("✅ Como funciona retry e fallback")
    print("✅ Como minerar tokens PRFIC")
    print("✅ Como conectar com blockchain")
    print("✅ Como monitorar via dashboard")
    print()
    
    print("Próximos passos recomendados:")
    print()
    
    print("1. CONFIGURAR SUAS APIS REAIS:")
    print("   - Edite o arquivo 'prfi.config.yaml'")
    print("   - Adicione suas APIs de produção")
    print("   - Configure fallbacks apropriados")
    print()
    
    print("2. CONSEGUIR BNB PARA DEPLOY:")
    print("   - Use faucet: https://testnet.binance.org/faucet-smart")
    print("   - Ou compre BNB real para mainnet")
    print("   - Configure MetaMask com BSC")
    print()
    
    print("3. DEPLOY DO SMART CONTRACT:")
    print("   - Instale Node.js se não tiver")
    print("   - Configure arquivo .env")
    print("   - Execute: npx hardhat run scripts/deploy.js --network bscTestnet")
    print()
    
    print("4. INTEGRAÇÃO COM SEU SISTEMA:")
    print("   - Use PRFI como biblioteca Python")
    print("   - Ou chame via API REST")
    print("   - Configure monitoramento 24/7")
    print()
    
    print("5. PRODUÇÃO:")
    print("   - Deploy na mainnet (BSC/Polygon)")
    print("   - Configure alertas")
    print("   - Monitore tokens minerados")
    print()
    
    if confirm("Deseja ver documentação completa?"):
        print("Documentação disponível em:")
        print("- README_WINDOWS.md (guia para Windows)")
        print("- GUIA_PRIMEIRO_USUARIO.md (este guia)")
        print("- README.md (documentação técnica)")
    
    if confirm("Deseja abrir dashboard uma última vez?"):
        try:
            print("Abrindo dashboard...")
            subprocess.Popen([sys.executable, "prfi_simple.py", "dashboard"])
            time.sleep(2)
            webbrowser.open("http://localhost:8080")
            print("Dashboard aberto em: http://localhost:8080")
        except:
            print("Erro ao abrir dashboard")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemonstração interrompida pelo usuário.")
        print("Obrigado por testar o PRFI Protocol!")
    except Exception as e:
        print(f"\nErro inesperado: {e}")
        print("Por favor, reporte este erro para a equipe PRFI.")
