#!/usr/bin/env python3
"""
PRFI CLI 2.0 - Crypto Utils
Geração de chaves criptográficas
"""

import secrets
import hashlib
from typing import Tuple

def generate_keypair() -> Tuple[str, str]:
    """Gerar par de chaves (privada, pública)"""
    # Gerar chave privada (32 bytes)
    private_key_bytes = secrets.token_bytes(32)
    private_key = "0x" + private_key_bytes.hex()
    
    # Gerar chave pública (derivada da privada para simplicidade)
    public_key_bytes = hashlib.sha256(private_key_bytes).digest()
    public_key = "0x" + public_key_bytes.hex()
    
    return private_key, public_key

def generate_api_key() -> str:
    """Gerar API key"""
    return secrets.token_urlsafe(32)

def generate_secret_key() -> str:
    """Gerar chave secreta"""
    return secrets.token_urlsafe(64)
