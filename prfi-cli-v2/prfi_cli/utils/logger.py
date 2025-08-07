#!/usr/bin/env python3
"""
PRFI CLI 2.0 - Logger Utils
Sistema de logging
"""

import logging
import sys
import os
from pathlib import Path
from rich.logging import RichHandler
from rich.console import Console

# Configurar encoding para Windows
if os.name == 'nt':  # Windows
    os.environ['PYTHONIOENCODING'] = 'utf-8'

def setup_logger(name: str = "prfi-cli", level: str = "INFO") -> logging.Logger:
    """Configurar logger com Rich handler"""
    
    # Criar logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Evitar duplicação de handlers
    if logger.handlers:
        return logger
    
    # Handler para console com Rich
    console_handler = RichHandler(
        rich_tracebacks=True,
        show_path=False,
        show_time=False
    )
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        "%(message)s"
    )
    console_handler.setFormatter(formatter)
    
    # Adicionar handler
    logger.addHandler(console_handler)
    
    return logger
