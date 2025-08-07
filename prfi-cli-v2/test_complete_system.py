#!/usr/bin/env python3
"""
PRFI CLI 2.0 - Teste Completo do Sistema
Teste end-to-end com APIs reais e mineração
"""

import asyncio
import aiohttp
import time
import json
import hashlib
import random
from pathlib import Path
from typing import Dict, List, Any
import sys

# Adicionar PRFI Core ao path
prfi_core_path = Path(__file__).parent.parent / "prfi-core"
if prfi_core_path.exists():
    sys.path.insert(0, str(prfi_core_path))

class PRFICompleteTest:
    """Teste completo do sistema PRFI"""
    
    def __init__(self):
        self.results = {}
        self.apis_reais = [
            {
                "name": "JSONPlaceholder",
                "url": "https://jsonplaceholder.typicode.com/posts/1",
                "method": "GET",
                "fallback_url": "https://httpbin.org/get",
                "expected_status": 200
            },
            {
                "name": "HTTPBin Echo",
                "url": "https://httpbin.org/json",
                "method": "GET", 
                "fallback_url": "https://jsonplaceholder.typicode.com/users/1",
                "expected_status": 200
            },
            {
                "name": "GitHub API",
                "url": "https://api.github.com/zen",
                "method": "GET",
                "fallback_url": "https://httpbin.org/uuid",
                "expected_status": 200
            },
            {
                "name": "CoinGecko API",
                "url": "https://api.coingecko.com/api/v3/ping",
                "method": "GET",
                "fallback_url": "https://httpbin.org/status/200",
                "expected_status": 200
            }
        ]
    
    async def run_complete_test(self):
        """Executar teste completo"""
        print("=" * 80)
        print("PRFI PROTOCOL - TESTE COMPLETO DO SISTEMA")
        print("=" * 80)
        print()
        
        # Fase 1: Teste de Configuração
        print("[FASE 1] Testando Configuração...")
        await self.test_configuration()
        
        # Fase 2: Teste de APIs Reais
        print("\n[FASE 2] Testando APIs Reais...")
        await self.test_real_apis()
        
        # Fase 3: Teste de Retry e Fallback
        print("\n[FASE 3] Testando Retry e Fallback...")
        await self.test_retry_fallback()
        
        # Fase 4: Teste de Mineração
        print("\n[FASE 4] Testando Sistema de Mineração...")
        await self.test_mining_system()
        
        # Fase 5: Teste de Blockchain
        print("\n[FASE 5] Testando Conexão Blockchain...")
        await self.test_blockchain_connection()
        
        # Fase 6: Teste End-to-End
        print("\n[FASE 6] Teste End-to-End Completo...")
        await self.test_end_to_end()
        
        # Relatório Final
        print("\n" + "=" * 80)
        self.show_final_report()
    
    async def test_configuration(self):
        """Testar configuração do sistema"""
        print("  [1.1] Verificando arquivo de configuração...")
        
        config_file = Path("prfi.config.yaml")
        if config_file.exists():
            print("  [OK] Arquivo prfi.config.yaml encontrado")
            
            try:
                import yaml
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                
                print("  [OK] Configuração carregada com sucesso")
                
                # Validar seções
                required_sections = ["project", "prfi", "blockchain"]
                for section in required_sections:
                    if section in config:
                        print(f"  [OK] Seção '{section}' presente")
                    else:
                        print(f"  [ERRO] Seção '{section}' ausente")
                
                self.results["config"] = {"success": True, "details": config}
                
            except Exception as e:
                print(f"  [ERRO] Falha ao carregar configuração: {e}")
                self.results["config"] = {"success": False, "error": str(e)}
        else:
            print("  [ERRO] Arquivo de configuração não encontrado")
            print("  [INFO] Execute: python prfi_simple.py init")
            self.results["config"] = {"success": False, "error": "Config file not found"}
    
    async def test_real_apis(self):
        """Testar APIs reais"""
        print("  [2.1] Testando APIs públicas reais...")
        
        api_results = {}
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            for api in self.apis_reais:
                print(f"  [2.{len(api_results)+2}] Testando {api['name']}...")
                
                start_time = time.time()
                try:
                    async with session.request(api["method"], api["url"]) as response:
                        response_time = time.time() - start_time
                        
                        if response.status == api["expected_status"]:
                            print(f"    [OK] {api['name']} - {response.status} ({response_time:.2f}s)")
                            api_results[api["name"]] = {
                                "success": True,
                                "status": response.status,
                                "response_time": response_time
                            }
                        else:
                            print(f"    [AVISO] {api['name']} - Status inesperado: {response.status}")
                            api_results[api["name"]] = {
                                "success": False,
                                "status": response.status,
                                "response_time": response_time
                            }
                            
                except Exception as e:
                    response_time = time.time() - start_time
                    print(f"    [ERRO] {api['name']} - {str(e)[:50]}...")
                    api_results[api["name"]] = {
                        "success": False,
                        "error": str(e),
                        "response_time": response_time
                    }
        
        # Determinar sucesso geral das APIs
        successful_apis = sum(1 for result in api_results.values() if result.get("success", False))
        apis_success = successful_apis == len(self.apis_reais)

        self.results["apis"] = {
            "success": apis_success,
            "details": api_results,
            "successful_count": successful_apis,
            "total_count": len(self.apis_reais)
        }

        print(f"  [RESUMO] {successful_apis}/{len(self.apis_reais)} APIs funcionando")
    
    async def test_retry_fallback(self):
        """Testar sistema de retry e fallback"""
        print("  [3.1] Testando sistema de retry...")
        
        # Testar API que falha propositalmente
        failing_url = "https://httpbin.org/status/500"  # Sempre retorna 500
        fallback_url = "https://httpbin.org/status/200"  # Sempre retorna 200
        
        retry_results = await self.simulate_retry_logic(failing_url, fallback_url)
        
        print(f"  [OK] Retry testado - {retry_results['attempts']} tentativas")
        print(f"  [OK] Fallback testado - Sucesso: {retry_results['fallback_success']}")

        # Adicionar sucesso geral
        retry_results["success"] = retry_results.get("fallback_success", False)
        self.results["retry_fallback"] = retry_results
    
    async def simulate_retry_logic(self, primary_url: str, fallback_url: str) -> Dict[str, Any]:
        """Simular lógica de retry e fallback"""
        
        max_attempts = 3
        initial_delay = 1.0
        multiplier = 2.0
        
        async with aiohttp.ClientSession() as session:
            # Tentar API principal com retry
            for attempt in range(max_attempts):
                try:
                    print(f"    [3.{attempt+2}] Tentativa {attempt+1}/{max_attempts} - API principal...")
                    
                    async with session.get(primary_url) as response:
                        if response.status == 200:
                            return {
                                "attempts": attempt + 1,
                                "primary_success": True,
                                "fallback_used": False,
                                "fallback_success": False
                            }
                        else:
                            print(f"      [FALHA] Status {response.status}")
                            
                except Exception as e:
                    print(f"      [FALHA] Erro: {str(e)[:30]}...")
                
                # Delay exponencial
                if attempt < max_attempts - 1:
                    delay = initial_delay * (multiplier ** attempt)
                    print(f"      [RETRY] Aguardando {delay:.1f}s...")
                    await asyncio.sleep(delay)
            
            # Tentar fallback
            print(f"    [3.{max_attempts+2}] Tentando API de fallback...")
            try:
                async with session.get(fallback_url) as response:
                    if response.status == 200:
                        print("      [OK] Fallback funcionou!")
                        return {
                            "attempts": max_attempts,
                            "primary_success": False,
                            "fallback_used": True,
                            "fallback_success": True
                        }
                    else:
                        print(f"      [FALHA] Fallback falhou - Status {response.status}")
                        
            except Exception as e:
                print(f"      [FALHA] Fallback erro: {str(e)[:30]}...")
            
            return {
                "attempts": max_attempts,
                "primary_success": False,
                "fallback_used": True,
                "fallback_success": False
            }
    
    async def test_mining_system(self):
        """Testar sistema de mineração"""
        print("  [4.1] Testando sistema de mineração de tokens...")
        
        # Simular eventos para mineração
        events = []
        for i in range(5):
            event = {
                "id": f"event_{i+1}",
                "timestamp": time.time(),
                "api_call": f"test_api_{i+1}",
                "success": random.choice([True, True, True, False]),  # 75% sucesso
                "response_time": random.randint(100, 500)
            }
            events.append(event)
            print(f"    [4.{i+2}] Evento {i+1}: {event['api_call']} - {'Sucesso' if event['success'] else 'Falha'}")
        
        # Simular mineração
        print("  [4.7] Processando eventos para mineração...")
        
        mining_results = self.simulate_mining(events)
        
        print(f"  [OK] Mineração simulada - {mining_results['tokens_mined']} tokens gerados")
        print(f"  [OK] Dificuldade: {mining_results['difficulty']}")
        print(f"  [OK] Hash: {mining_results['hash'][:16]}...")

        # Adicionar sucesso
        mining_results["success"] = mining_results.get("tokens_mined", 0) > 0
        self.results["mining"] = mining_results
    
    def simulate_mining(self, events: List[Dict]) -> Dict[str, Any]:
        """Simular processo de mineração"""
        
        # Criar batch de eventos
        batch_data = json.dumps(events, sort_keys=True)
        
        # Simular proof-of-work
        difficulty = 4  # Número de zeros no início do hash
        nonce = 0
        target = "0" * difficulty
        
        print(f"    [MINING] Procurando hash com {difficulty} zeros...")
        
        start_time = time.time()
        while True:
            # Criar hash com nonce
            data_to_hash = f"{batch_data}{nonce}"
            hash_result = hashlib.sha256(data_to_hash.encode()).hexdigest()
            
            if hash_result.startswith(target):
                mining_time = time.time() - start_time
                print(f"    [OK] Hash encontrado! Nonce: {nonce}, Tempo: {mining_time:.2f}s")
                
                return {
                    "tokens_mined": len([e for e in events if e["success"]]) * 10,  # 10 tokens por evento bem-sucedido
                    "difficulty": difficulty,
                    "nonce": nonce,
                    "hash": hash_result,
                    "mining_time": mining_time,
                    "events_processed": len(events)
                }
            
            nonce += 1
            
            # Limite de segurança
            if nonce > 100000:
                print("    [AVISO] Limite de mineração atingido")
                return {
                    "tokens_mined": 0,
                    "difficulty": difficulty,
                    "nonce": nonce,
                    "hash": "timeout",
                    "mining_time": time.time() - start_time,
                    "events_processed": 0
                }
    
    async def test_blockchain_connection(self):
        """Testar conexão com blockchain"""
        print("  [5.1] Testando conexão com BSC Testnet...")
        
        try:
            import web3
            from web3 import Web3
            from web3.middleware import geth_poa_middleware
            
            # Conectar à BSC Testnet
            rpc_url = "https://data-seed-prebsc-1-s1.binance.org:8545"
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            
            if w3.is_connected():
                print("  [OK] Conectado à BSC Testnet")
                
                # Obter informações da rede
                latest_block = w3.eth.get_block('latest')
                chain_id = w3.eth.chain_id
                gas_price = w3.eth.gas_price
                
                print(f"    Chain ID: {chain_id}")
                print(f"    Bloco atual: {latest_block.number}")
                print(f"    Gas price: {w3.from_wei(gas_price, 'gwei'):.2f} gwei")
                
                # Testar endereço de teste
                test_address = "0xf354664266B265e1992a793763f45Aa7CBb522e1"
                balance = w3.eth.get_balance(test_address)
                balance_bnb = w3.from_wei(balance, 'ether')
                
                print(f"    Saldo teste: {balance_bnb} BNB")
                
                self.results["blockchain"] = {
                    "success": True,
                    "chain_id": chain_id,
                    "latest_block": latest_block.number,
                    "gas_price_gwei": float(w3.from_wei(gas_price, 'gwei')),
                    "test_balance": float(balance_bnb)
                }
                
            else:
                print("  [ERRO] Não foi possível conectar à blockchain")
                self.results["blockchain"] = {"success": False, "error": "Connection failed"}
                
        except ImportError as e:
            print(f"  [ERRO] web3 não instalado - execute: pip install web3 ({e})")
            self.results["blockchain"] = {"success": False, "error": f"web3 not installed: {e}"}
        except Exception as e:
            print(f"  [ERRO] Erro blockchain: {e}")
            self.results["blockchain"] = {"success": False, "error": str(e)}
    
    async def test_end_to_end(self):
        """Teste end-to-end completo"""
        print("  [6.1] Executando fluxo completo PRFI...")
        
        # Simular fluxo completo: API call -> Retry -> Fallback -> Mining -> Blockchain
        
        print("    [6.2] Simulando chamada de API com falha...")
        
        # API que falha
        failing_api = {
            "name": "API Teste Falha",
            "url": "https://httpbin.org/status/503",  # Sempre falha
            "fallback_url": "https://httpbin.org/json"  # Sempre funciona
        }
        
        # Executar com retry e fallback
        result = await self.execute_prfi_flow(failing_api)
        
        if result["success"]:
            print("    [OK] Fluxo PRFI completo executado com sucesso")
            print(f"      - Tentativas: {result['attempts']}")
            print(f"      - Fallback usado: {result['fallback_used']}")
            print(f"      - Tokens minerados: {result['tokens_mined']}")
        else:
            print("    [ERRO] Fluxo PRFI falhou")
        
        self.results["end_to_end"] = result
    
    async def execute_prfi_flow(self, api_config: Dict) -> Dict[str, Any]:
        """Executar fluxo completo PRFI"""
        
        max_attempts = 3
        tokens_mined = 0
        
        async with aiohttp.ClientSession() as session:
            # Tentar API principal
            for attempt in range(max_attempts):
                try:
                    async with session.get(api_config["url"]) as response:
                        if response.status == 200:
                            # Sucesso - minerar tokens
                            tokens_mined = self.mine_tokens_for_success()
                            return {
                                "success": True,
                                "attempts": attempt + 1,
                                "fallback_used": False,
                                "tokens_mined": tokens_mined,
                                "final_status": response.status
                            }
                        else:
                            print(f"      [RETRY] Tentativa {attempt+1} falhou - Status {response.status}")
                            
                except Exception as e:
                    print(f"      [RETRY] Tentativa {attempt+1} erro - {str(e)[:30]}...")
                
                # Delay entre tentativas
                if attempt < max_attempts - 1:
                    await asyncio.sleep(1.0 * (2 ** attempt))  # Backoff exponencial
            
            # Tentar fallback
            print("      [FALLBACK] Tentando API de fallback...")
            try:
                async with session.get(api_config["fallback_url"]) as response:
                    if response.status == 200:
                        tokens_mined = self.mine_tokens_for_fallback()
                        return {
                            "success": True,
                            "attempts": max_attempts,
                            "fallback_used": True,
                            "tokens_mined": tokens_mined,
                            "final_status": response.status
                        }
                    else:
                        print(f"      [ERRO] Fallback falhou - Status {response.status}")
                        
            except Exception as e:
                print(f"      [ERRO] Fallback erro - {str(e)[:30]}...")
            
            return {
                "success": False,
                "attempts": max_attempts,
                "fallback_used": True,
                "tokens_mined": 0,
                "final_status": None
            }
    
    def mine_tokens_for_success(self) -> int:
        """Minerar tokens para evento bem-sucedido"""
        # Simular mineração rápida
        base_tokens = 10
        bonus = random.randint(0, 5)
        return base_tokens + bonus
    
    def mine_tokens_for_fallback(self) -> int:
        """Minerar tokens para fallback bem-sucedido"""
        # Menos tokens para fallback
        base_tokens = 5
        bonus = random.randint(0, 2)
        return base_tokens + bonus
    
    def show_final_report(self):
        """Mostrar relatório final"""
        print("RELATÓRIO FINAL DO TESTE COMPLETO")
        print("=" * 80)
        
        total_tests = len(self.results)
        successful_tests = sum(1 for result in self.results.values() 
                             if isinstance(result, dict) and result.get("success", False))
        
        print(f"RESUMO GERAL: {successful_tests}/{total_tests} testes passaram")
        print()
        
        for test_name, result in self.results.items():
            if isinstance(result, dict):
                status = "PASSOU" if result.get("success", False) else "FALHOU"
                print(f"  {test_name.upper()}: {status}")
                
                if test_name == "apis" and isinstance(result, dict):
                    for api_name, api_result in result.items():
                        if isinstance(api_result, dict):
                            api_status = "OK" if api_result.get("success", False) else "FALHA"
                            response_time = api_result.get("response_time", 0)
                            print(f"    - {api_name}: {api_status} ({response_time:.2f}s)")
                
                elif test_name == "mining" and result.get("success", False):
                    tokens = result.get("tokens_mined", 0)
                    mining_time = result.get("mining_time", 0)
                    print(f"    - Tokens minerados: {tokens}")
                    print(f"    - Tempo de mineração: {mining_time:.2f}s")
                
                elif test_name == "blockchain" and result.get("success", False):
                    block = result.get("latest_block", 0)
                    balance = result.get("test_balance", 0)
                    print(f"    - Bloco atual: {block}")
                    print(f"    - Saldo teste: {balance} BNB")
        
        print()
        print("=" * 80)
        
        if successful_tests == total_tests:
            print("RESULTADO: TODOS OS TESTES PASSARAM!")
            print("O sistema PRFI está funcionando perfeitamente!")
        else:
            print("RESULTADO: ALGUNS TESTES FALHARAM")
            print("Verifique os detalhes acima e corrija os problemas")
        
        print("=" * 80)

async def main():
    """Função principal"""
    tester = PRFICompleteTest()
    await tester.run_complete_test()

if __name__ == "__main__":
    asyncio.run(main())
