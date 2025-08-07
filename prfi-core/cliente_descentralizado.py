"""
Cliente PRFI Descentralizado - Versão sem minter central
Cada empresa minera seus próprios tokens através de prova de trabalho
"""

import asyncio
import hashlib
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from web3 import Web3
from eth_account import Account
import aiohttp
import json
import os

from .modelos import PRFIRequest, PRFIResponse
from .retry import RetryManager
from .excecoes import PRFIException


@dataclass
class MiningResult:
    """Resultado da mineração de um bloco"""
    nonce: int
    block_hash: str
    difficulty: int
    mining_time: float
    events_count: int


@dataclass
class ProofOfWork:
    """Prova de trabalho para um lote de eventos"""
    batch_id: str
    events_count: int
    merkle_root: str
    nonce: int
    block_hash: str
    company_address: str
    timestamp: int


class PRFIClientDescentralizado:
    """
    Cliente PRFI descentralizado que permite auto-mineração
    Cada empresa pode mintar seus próprios tokens
    """
    
    def __init__(
        self,
        company_private_key: str,
        contract_address: str,
        rpc_url: str = "https://bsc-dataseed1.binance.org",
        api_key: Optional[str] = None,
        max_retries: int = 3,
        min_difficulty: int = 4
    ):
        """
        Inicializar cliente descentralizado
        
        Args:
            company_private_key: Chave privada da empresa
            contract_address: Endereço do contrato PRFIC
            rpc_url: URL do RPC da blockchain
            api_key: Chave da API (opcional)
            max_retries: Máximo de tentativas de retry
            min_difficulty: Dificuldade mínima para prova de trabalho
        """
        self.private_key = company_private_key
        self.contract_address = contract_address
        self.rpc_url = rpc_url
        self.api_key = api_key
        self.max_retries = max_retries
        self.min_difficulty = min_difficulty
        
        # Configurar Web3
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = Account.from_key(company_private_key)
        self.company_address = self.account.address
        
        # Carregar ABI do contrato
        self.contract = self._load_contract()
        
        # Configurar retry manager
        self.retry_manager = RetryManager(max_retries=max_retries)
        
        # Estatísticas
        self.total_requests = 0
        self.successful_requests = 0
        self.tokens_earned = 0
        self.blocks_mined = 0
    
    def _load_contract(self):
        """Carregar contrato PRFIC"""
        # ABI simplificada do contrato
        abi = [
            {
                "inputs": [
                    {"name": "batchId", "type": "string"},
                    {"name": "eventsCount", "type": "uint256"},
                    {"name": "nonce", "type": "uint256"},
                    {"name": "merkleRoot", "type": "bytes32"}
                ],
                "name": "mintBatch",
                "outputs": [],
                "type": "function"
            },
            {
                "inputs": [{"name": "name", "type": "string"}],
                "name": "selfRegisterCompany",
                "outputs": [],
                "type": "function"
            },
            {
                "inputs": [{"name": "company", "type": "address"}],
                "name": "getCompanyStats",
                "outputs": [
                    {"name": "events", "type": "uint256"},
                    {"name": "tokens", "type": "uint256"},
                    {"name": "registered", "type": "bool"},
                    {"name": "name", "type": "string"},
                    {"name": "nonce", "type": "uint256"}
                ],
                "type": "function"
            }
        ]
        
        return self.w3.eth.contract(
            address=self.contract_address,
            abi=abi
        )
    
    async def register_company(self, company_name: str) -> bool:
        """
        Registrar empresa no sistema (auto-registro)
        
        Args:
            company_name: Nome da empresa
            
        Returns:
            True se registrado com sucesso
        """
        try:
            # Verificar se já está registrada
            stats = await self.get_company_stats()
            if stats['registered']:
                print(f"Empresa {company_name} já está registrada")
                return True
            
            # Construir transação
            tx = self.contract.functions.selfRegisterCompany(company_name).build_transaction({
                'from': self.company_address,
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.company_address)
            })
            
            # Assinar e enviar
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Aguardar confirmação
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                print(f"Empresa {company_name} registrada com sucesso!")
                return True
            else:
                print(f"Falha ao registrar empresa: {receipt}")
                return False
                
        except Exception as e:
            print(f"Erro ao registrar empresa: {e}")
            return False
    
    async def request(
        self,
        url: str,
        method: str = "GET",
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        fallback_url: Optional[str] = None,
        **kwargs
    ) -> PRFIResponse:
        """
        Fazer requisição HTTP com retry/fallback e mineração automática
        
        Args:
            url: URL da requisição
            method: Método HTTP
            data: Dados da requisição
            headers: Headers HTTP
            fallback_url: URL de fallback
            **kwargs: Argumentos adicionais
            
        Returns:
            Resposta PRFI com informações de mineração
        """
        self.total_requests += 1
        
        # Criar requisição
        request = PRFIRequest(
            url=url,
            method=method,
            data=data or {},
            headers=headers or {},
            fallback_url=fallback_url
        )
        
        # Executar com retry
        response = await self.retry_manager.execute_with_retry(
            self._make_http_request,
            request
        )
        
        # Se bem-sucedida, minerar bloco
        if response.success:
            self.successful_requests += 1
            await self._mine_block_for_response(response)
        
        return response
    
    async def _make_http_request(self, request: PRFIRequest) -> PRFIResponse:
        """Fazer requisição HTTP"""
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method=request.method,
                    url=request.url,
                    json=request.data if request.method.upper() in ['POST', 'PUT', 'PATCH'] else None,
                    params=request.data if request.method.upper() == 'GET' else None,
                    headers=request.headers
                ) as resp:
                    response_data = await resp.json() if resp.content_type == 'application/json' else await resp.text()
                    
                    return PRFIResponse(
                        success=resp.status == 200,
                        status_code=resp.status,
                        data=response_data,
                        response_time=time.time() - start_time,
                        url=request.url,
                        retries_used=0,
                        fallback_used=False
                    )
                    
            except Exception as e:
                return PRFIResponse(
                    success=False,
                    status_code=0,
                    data={"error": str(e)},
                    response_time=time.time() - start_time,
                    url=request.url,
                    retries_used=0,
                    fallback_used=False
                )
    
    async def _mine_block_for_response(self, response: PRFIResponse) -> Optional[MiningResult]:
        """
        Minerar bloco para uma resposta bem-sucedida
        
        Args:
            response: Resposta HTTP bem-sucedida
            
        Returns:
            Resultado da mineração ou None se falhou
        """
        try:
            # Gerar ID único do lote
            batch_id = self._generate_batch_id(response)
            
            # Criar merkle root dos eventos
            merkle_root = self._calculate_merkle_root([response.data])
            
            # Minerar bloco
            mining_result = await self._mine_block(
                batch_id=batch_id,
                events_count=1000,  # 1000 eventos = 1 token
                merkle_root=merkle_root
            )
            
            if mining_result:
                # Submeter para blockchain
                success = await self._submit_block_to_blockchain(
                    batch_id=batch_id,
                    events_count=1000,
                    nonce=mining_result.nonce,
                    merkle_root=merkle_root
                )
                
                if success:
                    self.tokens_earned += 0.8  # 80% para empresa
                    self.blocks_mined += 1
                    print(f"✅ Bloco minerado e submetido! Tokens ganhos: +0.8 PRFIC")
                    return mining_result
            
            return None
            
        except Exception as e:
            print(f"Erro na mineração: {e}")
            return None
    
    async def _mine_block(
        self,
        batch_id: str,
        events_count: int,
        merkle_root: str
    ) -> Optional[MiningResult]:
        """
        Minerar bloco com prova de trabalho
        
        Args:
            batch_id: ID do lote
            events_count: Número de eventos
            merkle_root: Raiz Merkle dos eventos
            
        Returns:
            Resultado da mineração
        """
        start_time = time.time()
        nonce = 0
        max_iterations = 1000000  # Limite para evitar loop infinito
        
        print(f"🔨 Iniciando mineração do bloco {batch_id}...")
        
        while nonce < max_iterations:
            # Gerar hash do bloco
            block_hash = self._generate_block_hash(
                batch_id, events_count, nonce, merkle_root
            )
            
            # Verificar se atende à dificuldade
            difficulty = self._calculate_difficulty(block_hash)
            
            if difficulty >= self.min_difficulty:
                mining_time = time.time() - start_time
                
                result = MiningResult(
                    nonce=nonce,
                    block_hash=block_hash,
                    difficulty=difficulty,
                    mining_time=mining_time,
                    events_count=events_count
                )
                
                print(f"⛏️  Bloco minerado! Nonce: {nonce}, Dificuldade: {difficulty}, Tempo: {mining_time:.2f}s")
                return result
            
            nonce += 1
            
            # Log de progresso
            if nonce % 10000 == 0:
                print(f"🔍 Minerando... Nonce: {nonce}")
        
        print(f"❌ Mineração falhou após {max_iterations} tentativas")
        return None
    
    def _generate_block_hash(
        self,
        batch_id: str,
        events_count: int,
        nonce: int,
        merkle_root: str
    ) -> str:
        """Gerar hash do bloco"""
        timestamp_hour = int(time.time()) // 3600  # Hora atual
        
        data = f"{self.company_address}{batch_id}{events_count}{nonce}{merkle_root}{timestamp_hour}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _calculate_difficulty(self, block_hash: str) -> int:
        """Calcular dificuldade (zeros à esquerda)"""
        difficulty = 0
        for char in block_hash:
            if char == '0':
                difficulty += 1
            else:
                break
        return difficulty
    
    def _generate_batch_id(self, response: PRFIResponse) -> str:
        """Gerar ID único do lote"""
        data = f"{response.url}{response.status_code}{time.time()}{self.company_address}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def _calculate_merkle_root(self, events: List) -> str:
        """Calcular raiz Merkle dos eventos"""
        if not events:
            return "0" * 64
        
        # Simplificado: hash de todos os eventos
        events_str = json.dumps(events, sort_keys=True)
        return hashlib.sha256(events_str.encode()).hexdigest()
    
    async def _submit_block_to_blockchain(
        self,
        batch_id: str,
        events_count: int,
        nonce: int,
        merkle_root: str
    ) -> bool:
        """Submeter bloco para blockchain"""
        try:
            # Converter merkle_root para bytes32
            merkle_root_bytes = bytes.fromhex(merkle_root)
            
            # Construir transação
            tx = self.contract.functions.mintBatch(
                batch_id,
                events_count,
                nonce,
                merkle_root_bytes
            ).build_transaction({
                'from': self.company_address,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.company_address)
            })
            
            # Assinar e enviar
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            print(f"📤 Transação enviada: {tx_hash.hex()}")
            
            # Aguardar confirmação
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                print(f"✅ Bloco confirmado na blockchain!")
                return True
            else:
                print(f"❌ Transação falhou: {receipt}")
                return False
                
        except Exception as e:
            print(f"Erro ao submeter bloco: {e}")
            return False
    
    async def get_company_stats(self) -> Dict:
        """Obter estatísticas da empresa"""
        try:
            stats = self.contract.functions.getCompanyStats(self.company_address).call()
            
            return {
                'events': stats[0],
                'tokens': stats[1],
                'registered': stats[2],
                'name': stats[3],
                'nonce': stats[4],
                'address': self.company_address
            }
            
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return {
                'events': 0,
                'tokens': 0,
                'registered': False,
                'name': '',
                'nonce': 0,
                'address': self.company_address
            }
    
    def get_local_stats(self) -> Dict:
        """Obter estatísticas locais"""
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'success_rate': self.successful_requests / max(self.total_requests, 1) * 100,
            'tokens_earned': self.tokens_earned,
            'blocks_mined': self.blocks_mined,
            'company_address': self.company_address
        }
