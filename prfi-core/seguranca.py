"""
Módulo de segurança para assinatura HMAC e validação.
"""

import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from .excecoes import InvalidSignatureException


class SecurityManager:
    """Gerenciador de segurança para assinatura e validação HMAC."""
    
    def __init__(self, secret_key: str, signature_validity_window: int = 300):
        """
        Inicializa o gerenciador de segurança.
        
        Args:
            secret_key: Chave secreta para assinatura HMAC
            signature_validity_window: Janela de validade em segundos (default: 5 min)
        """
        self.secret_key = secret_key.encode('utf-8')
        self.signature_validity_window = signature_validity_window
    
    def generate_nonce(self, length: int = 16) -> str:
        """Gera um nonce aleatório."""
        return secrets.token_hex(length)
    
    def generate_signature(self, payload: Dict[str, Any], nonce: Optional[str] = None) -> str:
        """
        Gera assinatura HMAC-SHA256 para o payload.
        
        Args:
            payload: Dados a serem assinados
            nonce: Nonce opcional para prevenir replay
            
        Returns:
            Assinatura no formato 'sha256=<hex>'
        """
        # Remove signature field if present
        clean_payload = {k: v for k, v in payload.items() if k != 'prfi_signature'}
        
        # Serialize to JSON with sorted keys for consistency
        json_str = json.dumps(clean_payload, sort_keys=True, separators=(',', ':'))
        
        # Add nonce if present
        if nonce:
            json_str += nonce
        
        # Calculate HMAC
        signature = hmac.new(
            self.secret_key,
            json_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"
    
    def verify_signature(
        self, 
        payload: Dict[str, Any], 
        received_signature: str,
        nonce: Optional[str] = None
    ) -> bool:
        """
        Verifica se a assinatura é válida.
        
        Args:
            payload: Dados recebidos
            received_signature: Assinatura recebida
            nonce: Nonce usado na assinatura
            
        Returns:
            True se a assinatura for válida
            
        Raises:
            InvalidSignatureException: Se a assinatura for inválida
        """
        try:
            expected_signature = self.generate_signature(payload, nonce)
            
            # Use constant-time comparison to prevent timing attacks
            is_valid = hmac.compare_digest(expected_signature, received_signature)
            
            if not is_valid:
                raise InvalidSignatureException(
                    event_id=payload.get('prfi_event_id')
                )
            
            return True
            
        except Exception as e:
            if isinstance(e, InvalidSignatureException):
                raise
            raise InvalidSignatureException(
                event_id=payload.get('prfi_event_id')
            )
    
    def verify_timestamp(self, timestamp_str: str) -> bool:
        """
        Verifica se o timestamp está dentro da janela de validade.
        
        Args:
            timestamp_str: Timestamp em formato ISO 8601
            
        Returns:
            True se o timestamp for válido
        """
        try:
            # Parse timestamp
            event_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            current_time = datetime.utcnow().replace(tzinfo=event_time.tzinfo)
            
            # Check if within validity window
            time_diff = abs((current_time - event_time).total_seconds())
            
            return time_diff <= self.signature_validity_window
            
        except (ValueError, TypeError):
            return False
    
    def sign_payload(self, payload: Dict[str, Any], include_nonce: bool = True) -> Dict[str, Any]:
        """
        Assina um payload completo adicionando signature e nonce.
        
        Args:
            payload: Payload a ser assinado
            include_nonce: Se deve incluir nonce
            
        Returns:
            Payload com signature e nonce adicionados
        """
        # Create a copy to avoid modifying original
        signed_payload = payload.copy()
        
        # Add nonce if requested
        nonce = None
        if include_nonce:
            nonce = self.generate_nonce()
            signed_payload['prfi_nonce'] = nonce
        
        # Generate and add signature
        signature = self.generate_signature(signed_payload, nonce)
        signed_payload['prfi_signature'] = signature
        
        return signed_payload
    
    def validate_payload(self, payload: Dict[str, Any], verify_timestamp: bool = True) -> bool:
        """
        Valida um payload completo (assinatura + timestamp).
        
        Args:
            payload: Payload a ser validado
            verify_timestamp: Se deve verificar o timestamp
            
        Returns:
            True se o payload for válido
            
        Raises:
            InvalidSignatureException: Se a validação falhar
        """
        # Check required fields
        required_fields = ['prfi_signature', 'prfi_timestamp']
        for field in required_fields:
            if field not in payload:
                raise InvalidSignatureException(
                    event_id=payload.get('prfi_event_id')
                )
        
        # Verify timestamp if requested
        if verify_timestamp:
            if not self.verify_timestamp(payload['prfi_timestamp']):
                raise InvalidSignatureException(
                    event_id=payload.get('prfi_event_id')
                )
        
        # Verify signature
        nonce = payload.get('prfi_nonce')
        return self.verify_signature(
            payload, 
            payload['prfi_signature'], 
            nonce
        )


def create_security_manager(secret_key: str, **kwargs) -> SecurityManager:
    """Factory function para criar SecurityManager."""
    return SecurityManager(secret_key, **kwargs)
