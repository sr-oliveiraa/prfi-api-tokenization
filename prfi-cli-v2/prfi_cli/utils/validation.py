#!/usr/bin/env python3
"""
PRFI CLI 2.0 - Validation Utils
Validação de configurações
"""

from typing import Dict, Any
from .config import ValidationResult

def validate_config(config: Dict[str, Any]) -> ValidationResult:
    """Validar configuração completa"""
    errors = []
    warnings = []
    
    # Validar estrutura básica
    required_sections = ["project", "prfi"]
    for section in required_sections:
        if section not in config:
            errors.append(f"Seção obrigatória '{section}' não encontrada")
    
    # Validar projeto
    if "project" in config:
        project_errors = validate_project_section(config["project"])
        errors.extend(project_errors)
    
    # Validar PRFI
    if "prfi" in config:
        prfi_errors, prfi_warnings = validate_prfi_section(config["prfi"])
        errors.extend(prfi_errors)
        warnings.extend(prfi_warnings)
    
    # Validar blockchain
    if "blockchain" in config:
        blockchain_warnings = validate_blockchain_section(config["blockchain"])
        warnings.extend(blockchain_warnings)
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )

def validate_project_section(project: Dict[str, Any]) -> list:
    """Validar seção do projeto"""
    errors = []
    
    if not project.get("name"):
        errors.append("Nome do projeto é obrigatório")
    elif len(project["name"]) < 3:
        errors.append("Nome do projeto deve ter pelo menos 3 caracteres")
    
    if not project.get("version"):
        errors.append("Versão do projeto é obrigatória")
    
    return errors

def validate_prfi_section(prfi: Dict[str, Any]) -> tuple:
    """Validar seção PRFI"""
    errors = []
    warnings = []
    
    # Validar retry
    if "retry" in prfi:
        retry = prfi["retry"]
        if retry.get("max_attempts", 0) <= 0:
            errors.append("max_attempts deve ser maior que 0")
        elif retry.get("max_attempts", 0) > 20:
            warnings.append("max_attempts muito alto pode causar lentidão")
        
        if retry.get("initial_delay", 0) <= 0:
            errors.append("initial_delay deve ser maior que 0")
        
        if retry.get("max_delay", 0) <= retry.get("initial_delay", 1):
            errors.append("max_delay deve ser maior que initial_delay")
    
    # Validar fallback
    if "fallback" in prfi:
        fallback = prfi["fallback"]
        if not isinstance(fallback.get("enabled"), bool):
            errors.append("fallback.enabled deve ser true ou false")
    
    # Validar tokenization
    if "tokenization" in prfi:
        tokenization = prfi["tokenization"]
        if tokenization.get("min_difficulty", 0) < 1:
            errors.append("min_difficulty deve ser pelo menos 1")
        elif tokenization.get("min_difficulty", 0) > 10:
            warnings.append("min_difficulty muito alto pode ser lento")
    
    return errors, warnings

def validate_blockchain_section(blockchain: Dict[str, Any]) -> list:
    """Validar seção blockchain"""
    warnings = []
    
    valid_networks = ["bsc-testnet", "bsc-mainnet", "polygon-mumbai", "polygon-mainnet"]
    network = blockchain.get("network")
    
    if network and network not in valid_networks:
        warnings.append(f"Rede '{network}' pode não ser suportada")
    
    if network and network.endswith("-mainnet"):
        warnings.append("Usando rede mainnet - certifique-se de ter fundos reais")
    
    return warnings
