#!/usr/bin/env python3
"""
PRFI CLI 2.0 - Instalador Simples
Script para instalar e configurar o PRFI CLI
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 PRFI CLI 2.0 - Instalador")
    print("=" * 50)
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ é necessário")
        sys.exit(1)
    
    print("✅ Python version OK")
    
    # Instalar dependências
    print("📦 Instalando dependências...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "click", "rich", "inquirer", "pyyaml", "fastapi", "uvicorn"
        ], check=True)
        print("✅ Dependências instaladas")
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar dependências")
        sys.exit(1)
    
    # Criar alias/script
    create_prfi_script()
    
    print("\n🎉 Instalação concluída!")
    print("\n🎯 Como usar:")
    print("python prfi.py --help")
    print("python prfi.py init --quick")
    print("python prfi.py dashboard")

def create_prfi_script():
    """Criar script prfi.py para facilitar uso"""
    script_content = '''#!/usr/bin/env python3
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
'''
    
    script_path = Path("prfi.py")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print(f"✅ Script criado: {script_path}")

if __name__ == "__main__":
    main()
