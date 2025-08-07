#!/usr/bin/env python3
"""
PRFI CLI 2.0 - Configuration Utils
Gerenciamento de configurações
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console

console = Console()

class ConfigError(Exception):
    """Erro de configuração"""
    pass

def get_config_path(custom_path: Optional[str] = None) -> Path:
    """Obter caminho do arquivo de configuração"""
    if custom_path:
        return Path(custom_path)
    
    # Procurar arquivo de config na ordem de prioridade
    possible_paths = [
        Path.cwd() / "prfi.config.yaml",
        Path.cwd() / "prfi.config.yml", 
        Path.cwd() / "prfi.config.json",
        Path.home() / ".prfi" / "config.yaml",
        Path.home() / ".config" / "prfi" / "config.yaml"
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    # Retornar padrão se não encontrar
    return Path.cwd() / "prfi.config.yaml"

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Carregar configuração do arquivo"""
    path = get_config_path(config_path)
    
    if not path.exists():
        raise ConfigError(f"Arquivo de configuração não encontrado: {path}")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix.lower() == '.json':
                return json.load(f)
            else:
                return yaml.safe_load(f) or {}
    except Exception as e:
        raise ConfigError(f"Erro ao carregar configuração: {e}")

def save_config(config: Dict[str, Any], output_path: Optional[str] = None) -> Path:
    """Salvar configuração no arquivo"""
    path = get_config_path(output_path)
    
    # Criar diretório se não existir
    path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(path, 'w', encoding='utf-8') as f:
            if path.suffix.lower() == '.json':
                json.dump(config, f, indent=2, ensure_ascii=False)
            else:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True, indent=2)
        
        return path
    except Exception as e:
        raise ConfigError(f"Erro ao salvar configuração: {e}")

def get_default_config() -> Dict[str, Any]:
    """Obter configuração padrão"""
    return {
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

def validate_config(config: Dict[str, Any]) -> 'ValidationResult':
    """Validar configuração"""
    errors = []
    warnings = []
    
    # Validar estrutura básica
    required_sections = ["project", "prfi", "blockchain"]
    for section in required_sections:
        if section not in config:
            errors.append(f"Seção obrigatória '{section}' não encontrada")
    
    # Validar projeto
    if "project" in config:
        project = config["project"]
        if not project.get("name"):
            errors.append("Nome do projeto é obrigatório")
    
    # Validar PRFI
    if "prfi" in config:
        prfi = config["prfi"]
        if "retry" in prfi:
            retry = prfi["retry"]
            if retry.get("max_attempts", 0) <= 0:
                errors.append("max_attempts deve ser maior que 0")
            if retry.get("initial_delay", 0) <= 0:
                errors.append("initial_delay deve ser maior que 0")
    
    # Validar blockchain
    if "blockchain" in config:
        blockchain = config["blockchain"]
        valid_networks = ["bsc-testnet", "bsc-mainnet", "polygon-mumbai", "polygon-mainnet"]
        if blockchain.get("network") not in valid_networks:
            warnings.append(f"Rede '{blockchain.get('network')}' pode não ser suportada")
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )

class ValidationResult:
    """Resultado da validação"""
    def __init__(self, valid: bool, errors: list, warnings: list):
        self.valid = valid
        self.errors = errors
        self.warnings = warnings
