#!/usr/bin/env python3
"""
PRFI CLI 2.0 - Network Utils
Utilitários de rede
"""

import socket
from typing import Optional

def find_free_port(start_port: int = 8080) -> int:
    """Encontrar porta livre"""
    port = start_port
    while port < start_port + 100:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            port += 1
    
    raise RuntimeError("Não foi possível encontrar porta livre")

def get_local_ip() -> str:
    """Obter IP local"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
