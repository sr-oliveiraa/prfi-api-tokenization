"""
Sistema de criptografia e proof-of-work para PRFI
"""

import hashlib
import time
from typing import Tuple


class ProofOfWork:
    """Sistema de proof-of-work para mineração PRFI"""
    
    def __init__(self, difficulty: int = 4):
        """
        Inicializa o sistema de PoW
        
        Args:
            difficulty: Número de zeros necessários no início do hash
        """
        self.difficulty = difficulty
        self.target = "0" * difficulty
    
    def mine(self, data: str) -> Tuple[int, str]:
        """
        Minera um bloco encontrando um nonce válido
        
        Args:
            data: Dados para minerar
            
        Returns:
            Tuple com (nonce, hash_resultado)
        """
        nonce = 0
        start_time = time.time()
        
        while True:
            # Combinar dados com nonce
            block_data = f"{data}{nonce}"
            
            # Calcular hash
            hash_result = hashlib.sha256(block_data.encode()).hexdigest()
            
            # Verificar se atende à dificuldade
            if hash_result.startswith(self.target):
                mining_time = time.time() - start_time
                print(f"Bloco minerado! Nonce: {nonce}, Hash: {hash_result[:20]}..., Tempo: {mining_time:.2f}s")
                return nonce, hash_result
            
            nonce += 1
            
            # Log de progresso a cada 10000 tentativas
            if nonce % 10000 == 0:
                print(f"Minerando... Nonce: {nonce}")
    
    def verify(self, data: str, nonce: int, expected_hash: str) -> bool:
        """
        Verifica se um nonce é válido para os dados
        
        Args:
            data: Dados originais
            nonce: Nonce a verificar
            expected_hash: Hash esperado
            
        Returns:
            True se válido
        """
        block_data = f"{data}{nonce}"
        calculated_hash = hashlib.sha256(block_data.encode()).hexdigest()
        
        return (calculated_hash == expected_hash and 
                calculated_hash.startswith(self.target))


class DigitalSigner:
    """Sistema de assinatura digital para blocos"""
    
    def __init__(self, private_key_path: str, public_key_path: str):
        """
        Inicializa o sistema de assinatura
        
        Args:
            private_key_path: Caminho para chave privada
            public_key_path: Caminho para chave pública
        """
        self.private_key_path = private_key_path
        self.public_key_path = public_key_path
    
    def sign_data(self, data: str) -> str:
        """
        Assina dados com a chave privada
        
        Args:
            data: Dados para assinar
            
        Returns:
            Assinatura em hex
        """
        # Implementação simplificada - em produção usar RSA/ECDSA
        signature_data = f"signature_{hashlib.sha256(data.encode()).hexdigest()}"
        return hashlib.sha256(signature_data.encode()).hexdigest()
    
    def verify_signature(self, data: str, signature: str) -> bool:
        """
        Verifica uma assinatura
        
        Args:
            data: Dados originais
            signature: Assinatura a verificar
            
        Returns:
            True se válida
        """
        expected_signature = self.sign_data(data)
        return signature == expected_signature
    
    def get_public_key_string(self) -> str:
        """Retorna a chave pública como string"""
        return f"public_key_{hashlib.sha256(self.public_key_path.encode()).hexdigest()[:16]}"


def create_digital_signer(private_key_path: str, public_key_path: str) -> DigitalSigner:
    """
    Função de conveniência para criar um assinador digital
    
    Args:
        private_key_path: Caminho para chave privada
        public_key_path: Caminho para chave pública
        
    Returns:
        Instância do DigitalSigner
    """
    return DigitalSigner(private_key_path, public_key_path)
