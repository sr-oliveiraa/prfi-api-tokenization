#!/usr/bin/env python3
"""
PRFI CLI 2.0 - Script de Execução
"""

import sys
from pathlib import Path

# Adicionar diretório do CLI ao path
cli_dir = Path(__file__).parent / "prfi_cli"
sys.path.insert(0, str(cli_dir.parent))

# Importar e executar CLI
from prfi_cli.main import main

if __name__ == "__main__":
    main()
