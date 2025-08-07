"""
Módulo de integração com blockchain para tokenização PRFIC.

Este módulo implementa a integração real com a blockchain Polygon
para mint e gerenciamento de tokens PRFIC usando Web3.py.
"""

import asyncio
import json
import logging
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal

import structlog
from web3 import Web3
from eth_account import Account

# Importar middleware com fallback para versões diferentes
try:
    from web3.middleware import geth_poa_middleware
except ImportError:
    try:
        from web3.middleware.geth_poa import geth_poa_middleware
    except ImportError:
        # Fallback para versões mais antigas
        geth_poa_middleware = None

from .modelos import TokenBatch


logger = structlog.get_logger(__name__)


# ABI do contrato PRFIC (será carregado do arquivo JSON)
PRFIC_ABI = None

def load_contract_abi() -> List[Dict]:
    """Carrega ABI do contrato PRFIC."""
    global PRFIC_ABI
    if PRFIC_ABI is None:
        try:
            # Tentar carregar do arquivo de build do Hardhat
            abi_path = "artifacts/contracts/PRFIC.sol/PRFIC.json"
            if os.path.exists(abi_path):
                with open(abi_path, 'r') as f:
                    contract_json = json.load(f)
                    PRFIC_ABI = contract_json['abi']
            else:
                # ABI mínima para funcionar sem arquivo
                PRFIC_ABI = [
                    {
                        "inputs": [
                            {"name": "batchId", "type": "string"},
                            {"name": "company", "type": "address"},
                            {"name": "eventsCount", "type": "uint256"}
                        ],
                        "name": "mintBatch",
                        "outputs": [],
                        "stateMutability": "nonpayable",
                        "type": "function"
                    },
                    {
                        "inputs": [
                            {"name": "company", "type": "address"},
                            {"name": "name", "type": "string"}
                        ],
                        "name": "registerCompany",
                        "outputs": [],
                        "stateMutability": "nonpayable",
                        "type": "function"
                    },
                    {
                        "inputs": [{"name": "account", "type": "address"}],
                        "name": "balanceOf",
                        "outputs": [{"name": "", "type": "uint256"}],
                        "stateMutability": "view",
                        "type": "function"
                    },
                    {
                        "inputs": [],
                        "name": "getGlobalStats",
                        "outputs": [
                            {"name": "_totalSupply", "type": "uint256"},
                            {"name": "_totalBatches", "type": "uint256"},
                            {"name": "_totalEvents", "type": "uint256"},
                            {"name": "_treasuryBalance", "type": "uint256"}
                        ],
                        "stateMutability": "view",
                        "type": "function"
                    },
                    {
                        "inputs": [{"name": "company", "type": "address"}],
                        "name": "getCompanyStats",
                        "outputs": [
                            {"name": "events", "type": "uint256"},
                            {"name": "tokens", "type": "uint256"},
                            {"name": "registered", "type": "bool"}
                        ],
                        "stateMutability": "view",
                        "type": "function"
                    }
                ]
        except Exception as e:
            logger.error("Erro ao carregar ABI do contrato", error=str(e))
            PRFIC_ABI = []

    return PRFIC_ABI


class BlockchainGateway:
    """Gateway real para interação com blockchain Polygon."""

    def __init__(
        self,
        private_key: Optional[str] = None,
        contract_address: Optional[str] = None,
        rpc_url: str = "https://polygon-rpc.com",
        chain_id: int = 137  # Polygon Mainnet
    ):
        """
        Inicializa o gateway blockchain.

        Args:
            private_key: Chave privada para transações (hex string)
            contract_address: Endereço do contrato PRFIC
            rpc_url: URL do RPC da blockchain
            chain_id: ID da chain (137 = Polygon, 80001 = Mumbai)
        """
        self.private_key = private_key
        self.contract_address = contract_address
        self.rpc_url = rpc_url
        self.chain_id = chain_id
        self.logger = logger.bind(component="blockchain_gateway")

        # Estado interno
        self._initialized = False
        self.w3: Optional[Web3] = None
        self.account: Optional[Account] = None
        self.contract = None

        # Configurações de gas
        self.gas_limit = 200000
        self.gas_price_gwei = 30
    
    async def initialize(self) -> None:
        """Inicializa conexão real com blockchain."""
        try:
            if not self.private_key:
                raise ValueError("Private key é obrigatória")

            if not self.contract_address:
                raise ValueError("Contract address é obrigatório")

            # Inicializar Web3
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))

            # Adicionar middleware para Polygon (PoA) se disponível
            if self.chain_id in [137, 80001] and geth_poa_middleware:  # Polygon networks
                self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

            # Verificar conexão
            if not self.w3.is_connected():
                raise ConnectionError(f"Não foi possível conectar ao RPC: {self.rpc_url}")

            # Configurar conta
            self.account = Account.from_key(self.private_key)

            # Verificar saldo
            balance = self.w3.eth.get_balance(self.account.address)
            balance_eth = self.w3.from_wei(balance, 'ether')

            if balance == 0:
                self.logger.warning(
                    "Conta sem saldo para gas",
                    address=self.account.address,
                    balance=balance_eth
                )

            # Carregar contrato
            contract_abi = load_contract_abi()
            if not contract_abi:
                raise ValueError("ABI do contrato não encontrada")

            self.contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contract_address),
                abi=contract_abi
            )

            # Verificar se o contrato existe
            code = self.w3.eth.get_code(self.contract.address)
            if code == b'':
                raise ValueError(f"Contrato não encontrado no endereço: {self.contract_address}")

            self._initialized = True

            self.logger.info(
                "Gateway blockchain inicializado com sucesso",
                contract_address=self.contract_address,
                account_address=self.account.address,
                balance_eth=float(balance_eth),
                chain_id=self.chain_id,
                rpc_url=self.rpc_url
            )

        except Exception as e:
            self.logger.error("Erro ao inicializar gateway blockchain", error=str(e))
            raise
    
    async def mint_tokens(
        self,
        company_address: str,
        amount: float,
        batch_id: str,
        events_count: int = 1000
    ) -> Dict[str, Any]:
        """
        Minta tokens PRFIC para uma empresa via smart contract.

        Args:
            company_address: Endereço da wallet da empresa
            amount: Quantidade de tokens a mintar (deve ser 1.0)
            batch_id: ID único do lote para referência
            events_count: Número de eventos (deve ser 1000)

        Returns:
            Dict com informações da transação
        """
        try:
            if not self._initialized:
                await self.initialize()

            # Validações
            if amount != 1.0:
                raise ValueError(f"Amount deve ser 1.0, recebido: {amount}")

            if events_count != 1000:
                raise ValueError(f"Events count deve ser 1000, recebido: {events_count}")

            company_checksum = Web3.to_checksum_address(company_address)

            self.logger.info(
                "Iniciando mint de tokens na blockchain",
                company_address=company_checksum,
                batch_id=batch_id,
                events_count=events_count
            )

            # Preparar transação
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            gas_price = self.w3.to_wei(self.gas_price_gwei, 'gwei')

            # Construir transação
            transaction = self.contract.functions.mintBatch(
                batch_id,
                company_checksum,
                events_count
            ).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': self.gas_limit,
                'gasPrice': gas_price,
                'chainId': self.chain_id
            })

            # Assinar transação
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)

            # Enviar transação
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_hash_hex = tx_hash.hex()

            self.logger.info(
                "Transação enviada",
                tx_hash=tx_hash_hex,
                company_address=company_checksum,
                batch_id=batch_id
            )

            # Aguardar confirmação
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)

            if receipt.status != 1:
                raise Exception(f"Transação falhou: {tx_hash_hex}")

            # Extrair informações da transação
            result = {
                "tx_hash": tx_hash_hex,
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "company_tokens": 0.8,  # 80% para empresa
                "developer_tokens": 0.2,  # 20% para desenvolvedor
                "status": "success",
                "events_count": events_count,
                "batch_id": batch_id,
                "company_address": company_checksum
            }

            self.logger.info(
                "Tokens mintados com sucesso na blockchain",
                tx_hash=tx_hash_hex,
                block_number=receipt.blockNumber,
                gas_used=receipt.gasUsed,
                company_address=company_checksum
            )

            return result

        except Exception as e:
            self.logger.error(
                "Erro ao mintar tokens na blockchain",
                company_address=company_address,
                batch_id=batch_id,
                error=str(e)
            )
            raise
    
    async def register_company(
        self,
        company_address: str,
        company_name: str
    ) -> Dict[str, Any]:
        """
        Registra uma empresa no smart contract.

        Args:
            company_address: Endereço da wallet da empresa
            company_name: Nome da empresa

        Returns:
            Dict com informações da transação
        """
        try:
            if not self._initialized:
                await self.initialize()

            company_checksum = Web3.to_checksum_address(company_address)

            self.logger.info(
                "Registrando empresa na blockchain",
                company_address=company_checksum,
                company_name=company_name
            )

            # Preparar transação
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            gas_price = self.w3.to_wei(self.gas_price_gwei, 'gwei')

            # Construir transação
            transaction = self.contract.functions.registerCompany(
                company_checksum,
                company_name
            ).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': self.gas_limit,
                'gasPrice': gas_price,
                'chainId': self.chain_id
            })

            # Assinar e enviar transação
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_hash_hex = tx_hash.hex()

            # Aguardar confirmação
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)

            if receipt.status != 1:
                raise Exception(f"Transação de registro falhou: {tx_hash_hex}")

            result = {
                "tx_hash": tx_hash_hex,
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "status": "success",
                "company_address": company_checksum,
                "company_name": company_name
            }

            self.logger.info(
                "Empresa registrada com sucesso na blockchain",
                tx_hash=tx_hash_hex,
                company_address=company_checksum,
                company_name=company_name
            )

            return result

        except Exception as e:
            self.logger.error(
                "Erro ao registrar empresa na blockchain",
                company_address=company_address,
                company_name=company_name,
                error=str(e)
            )
            raise
    
    async def get_token_balance(self, address: str) -> float:
        """
        Obtém saldo de tokens PRFIC de um endereço.

        Args:
            address: Endereço da wallet

        Returns:
            Saldo de tokens em PRFIC
        """
        try:
            if not self._initialized:
                await self.initialize()

            address_checksum = Web3.to_checksum_address(address)

            # Chamar função balanceOf do contrato
            balance_wei = self.contract.functions.balanceOf(address_checksum).call()

            # Converter de wei para PRFIC (18 decimais)
            balance_prfic = self.w3.from_wei(balance_wei, 'ether')

            return float(balance_prfic)

        except Exception as e:
            self.logger.error(
                "Erro ao consultar saldo na blockchain",
                address=address,
                error=str(e)
            )
            raise
    
    async def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """
        Verifica status de uma transação na blockchain.

        Args:
            tx_hash: Hash da transação

        Returns:
            Status da transação
        """
        try:
            if not self._initialized:
                await self.initialize()

            # Obter receipt da transação
            try:
                receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                transaction = self.w3.eth.get_transaction(tx_hash)

                # Obter bloco atual para calcular confirmações
                current_block = self.w3.eth.block_number
                confirmations = current_block - receipt.blockNumber

                status = "confirmed" if receipt.status == 1 else "failed"

                return {
                    "tx_hash": tx_hash,
                    "status": status,
                    "confirmations": confirmations,
                    "block_number": receipt.blockNumber,
                    "gas_used": receipt.gasUsed,
                    "gas_price": transaction.gasPrice,
                    "from_address": transaction["from"],
                    "to_address": transaction.to,
                    "value": transaction.value
                }

            except Exception:
                # Transação não encontrada ou pendente
                return {
                    "tx_hash": tx_hash,
                    "status": "pending",
                    "confirmations": 0,
                    "block_number": None
                }

        except Exception as e:
            self.logger.error(
                "Erro ao verificar transação na blockchain",
                tx_hash=tx_hash,
                error=str(e)
            )
            raise

    async def get_company_stats(self, company_address: str) -> Dict[str, Any]:
        """
        Obtém estatísticas de uma empresa do smart contract.

        Args:
            company_address: Endereço da empresa

        Returns:
            Dict com estatísticas da empresa
        """
        try:
            if not self._initialized:
                await self.initialize()

            company_checksum = Web3.to_checksum_address(company_address)

            # Chamar função getCompanyStats do contrato
            events, tokens, registered = self.contract.functions.getCompanyStats(
                company_checksum
            ).call()

            # Converter tokens de wei para PRFIC
            tokens_prfic = self.w3.from_wei(tokens, 'ether')

            return {
                "company_address": company_checksum,
                "total_events": events,
                "total_tokens": float(tokens_prfic),
                "registered": registered
            }

        except Exception as e:
            self.logger.error(
                "Erro ao obter estatísticas da empresa",
                company_address=company_address,
                error=str(e)
            )
            raise

    async def get_global_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas globais do smart contract.

        Returns:
            Dict com estatísticas globais
        """
        try:
            if not self._initialized:
                await self.initialize()

            # Chamar função getGlobalStats do contrato
            total_supply, total_batches, total_events, treasury_balance = (
                self.contract.functions.getGlobalStats().call()
            )

            # Converter valores de wei para PRFIC
            total_supply_prfic = self.w3.from_wei(total_supply, 'ether')
            treasury_balance_prfic = self.w3.from_wei(treasury_balance, 'ether')

            return {
                "total_supply": float(total_supply_prfic),
                "total_batches": total_batches,
                "total_events": total_events,
                "treasury_balance": float(treasury_balance_prfic),
                "contract_address": self.contract_address
            }

        except Exception as e:
            self.logger.error(
                "Erro ao obter estatísticas globais",
                error=str(e)
            )
            raise

    async def is_batch_processed(self, batch_id: str) -> bool:
        """
        Verifica se um lote já foi processado no smart contract.

        Args:
            batch_id: ID do lote

        Returns:
            True se já foi processado
        """
        try:
            if not self._initialized:
                await self.initialize()

            # Chamar função isBatchProcessed do contrato
            processed = self.contract.functions.isBatchProcessed(batch_id).call()

            return processed

        except Exception as e:
            self.logger.error(
                "Erro ao verificar se lote foi processado",
                batch_id=batch_id,
                error=str(e)
            )
            raise


class PRFICContract:
    """Wrapper de alto nível para interação com contrato PRFIC."""

    def __init__(self, gateway: BlockchainGateway):
        """
        Inicializa wrapper do contrato.

        Args:
            gateway: Gateway blockchain configurado
        """
        self.gateway = gateway
        self.logger = logger.bind(component="prfic_contract")

    async def mint_batch(
        self,
        company_address: str,
        batch_id: str,
        events_count: int = 1000
    ) -> Dict[str, Any]:
        """
        Minta 1 PRFIC para uma empresa após processar 1000 eventos.

        Args:
            company_address: Endereço da empresa
            batch_id: ID único do lote
            events_count: Número de eventos (deve ser 1000)

        Returns:
            Resultado da transação
        """
        return await self.gateway.mint_tokens(
            company_address=company_address,
            amount=1.0,  # Sempre 1 PRFIC por lote
            batch_id=batch_id,
            events_count=events_count
        )

    async def register_company(
        self,
        company_address: str,
        company_name: str
    ) -> Dict[str, Any]:
        """
        Registra uma empresa no contrato.

        Args:
            company_address: Endereço da empresa
            company_name: Nome da empresa

        Returns:
            Resultado da transação
        """
        return await self.gateway.register_company(company_address, company_name)

    async def get_balance(self, address: str) -> float:
        """
        Consulta saldo de tokens PRFIC de um endereço.

        Args:
            address: Endereço da wallet

        Returns:
            Saldo em PRFIC
        """
        return await self.gateway.get_token_balance(address)

    async def get_company_stats(self, company_address: str) -> Dict[str, Any]:
        """
        Obtém estatísticas de uma empresa.

        Args:
            company_address: Endereço da empresa

        Returns:
            Estatísticas da empresa
        """
        return await self.gateway.get_company_stats(company_address)

    async def get_global_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas globais do contrato.

        Returns:
            Estatísticas globais
        """
        return await self.gateway.get_global_stats()

    async def is_batch_processed(self, batch_id: str) -> bool:
        """
        Verifica se um lote já foi processado.

        Args:
            batch_id: ID do lote

        Returns:
            True se já foi processado
        """
        return await self.gateway.is_batch_processed(batch_id)

    async def get_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        """
        Verifica status de uma transação.

        Args:
            tx_hash: Hash da transação

        Returns:
            Status da transação
        """
        return await self.gateway.get_transaction_status(tx_hash)


# Factory functions e configurações
def create_blockchain_gateway(
    private_key: Optional[str] = None,
    contract_address: Optional[str] = None,
    rpc_url: str = "https://polygon-rpc.com",
    chain_id: int = 137,
    gas_price_gwei: int = 30
) -> BlockchainGateway:
    """
    Cria gateway blockchain configurado.

    Args:
        private_key: Chave privada para transações
        contract_address: Endereço do contrato PRFIC
        rpc_url: URL do RPC da blockchain
        chain_id: ID da chain (137 = Polygon, 80001 = Mumbai)
        gas_price_gwei: Preço do gas em gwei

    Returns:
        Gateway blockchain configurado
    """
    gateway = BlockchainGateway(private_key, contract_address, rpc_url, chain_id)
    gateway.gas_price_gwei = gas_price_gwei
    return gateway


def create_prfic_contract(gateway: BlockchainGateway) -> PRFICContract:
    """
    Cria wrapper do contrato PRFIC.

    Args:
        gateway: Gateway blockchain configurado

    Returns:
        Wrapper do contrato PRFIC
    """
    return PRFICContract(gateway)


def create_blockchain_from_env() -> BlockchainGateway:
    """
    Cria gateway blockchain usando variáveis de ambiente.

    Variáveis esperadas:
    - BLOCKCHAIN_PRIVATE_KEY: Chave privada
    - PRFIC_CONTRACT_ADDRESS: Endereço do contrato
    - BLOCKCHAIN_RPC_URL: URL do RPC (opcional)
    - BLOCKCHAIN_CHAIN_ID: ID da chain (opcional)
    - BLOCKCHAIN_GAS_PRICE: Preço do gas em gwei (opcional)

    Returns:
        Gateway blockchain configurado
    """
    private_key = os.getenv('BLOCKCHAIN_PRIVATE_KEY')
    contract_address = os.getenv('PRFIC_CONTRACT_ADDRESS')
    rpc_url = os.getenv('BLOCKCHAIN_RPC_URL', 'https://polygon-rpc.com')
    chain_id = int(os.getenv('BLOCKCHAIN_CHAIN_ID', '137'))
    gas_price = int(os.getenv('BLOCKCHAIN_GAS_PRICE', '30'))

    if not private_key:
        raise ValueError("BLOCKCHAIN_PRIVATE_KEY não definida")

    if not contract_address:
        raise ValueError("PRFIC_CONTRACT_ADDRESS não definido")

    return create_blockchain_gateway(
        private_key=private_key,
        contract_address=contract_address,
        rpc_url=rpc_url,
        chain_id=chain_id,
        gas_price_gwei=gas_price
    )


# Configurações de rede pré-definidas
NETWORK_CONFIGS = {
    'polygon': {
        'rpc_url': 'https://polygon-rpc.com',
        'chain_id': 137,
        'gas_price_gwei': 30,
        'name': 'Polygon Mainnet'
    },
    'mumbai': {
        'rpc_url': 'https://rpc-mumbai.maticvigil.com',
        'chain_id': 80001,
        'gas_price_gwei': 30,
        'name': 'Polygon Mumbai Testnet'
    },
    'localhost': {
        'rpc_url': 'http://127.0.0.1:8545',
        'chain_id': 31337,
        'gas_price_gwei': 20,
        'name': 'Local Hardhat Network'
    }
}


def create_blockchain_for_network(
    network: str,
    private_key: str,
    contract_address: str
) -> BlockchainGateway:
    """
    Cria gateway blockchain para uma rede específica.

    Args:
        network: Nome da rede ('polygon', 'mumbai', 'localhost')
        private_key: Chave privada
        contract_address: Endereço do contrato

    Returns:
        Gateway blockchain configurado
    """
    if network not in NETWORK_CONFIGS:
        raise ValueError(f"Rede não suportada: {network}. Opções: {list(NETWORK_CONFIGS.keys())}")

    config = NETWORK_CONFIGS[network]

    return create_blockchain_gateway(
        private_key=private_key,
        contract_address=contract_address,
        rpc_url=config['rpc_url'],
        chain_id=config['chain_id'],
        gas_price_gwei=config['gas_price_gwei']
    )
