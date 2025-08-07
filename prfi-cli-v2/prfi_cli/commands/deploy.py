#!/usr/bin/env python3
"""
PRFI CLI 2.0 - Deploy Command
Deploy de smart contracts integrado com PRFI-Core
"""

import click
import os
import sys
import subprocess
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
import time

from ..utils.config import load_config, ConfigError
from ..utils.banner import show_success_banner, show_error_banner

console = Console()

@click.command()
@click.option('--network', help='Rede blockchain (bsc-testnet, bsc-mainnet, etc)')
@click.option('--verify', is_flag=True, help='Verificar contrato no explorer')
@click.option('--dry-run', is_flag=True, help='Simular deploy sem executar')
@click.option('--gas-limit', type=int, help='Limite de gas customizado')
@click.option('--gas-price', help='Preço do gas (em gwei)')
def deploy(network, verify, dry_run, gas_limit, gas_price):
    """🚀 Deploy do smart contract PRFIC"""

    console.print("🚀 [bold blue]PRFI Protocol - Deploy Real[/bold blue]")
    console.print("Integrando com PRFI-Core para deploy completo...\n")

    if dry_run:
        console.print("🧪 [yellow]Modo simulação ativado - nenhuma transação será enviada[/yellow]\n")

    try:
        # Carregar configuração
        config = load_config()

        # Determinar rede
        target_network = network or config.get("blockchain", {}).get("network", "bsc-testnet")

        # Executar deploy
        success = execute_deploy(config, target_network, verify, dry_run, gas_limit, gas_price)

        if success:
            show_success_banner(
                "Deploy Concluído com Sucesso!",
                f"Smart contract PRFIC deployado na rede {target_network}"
            )
        else:
            show_error_banner(
                "Deploy Falhou",
                "Verifique os logs acima para mais detalhes"
            )
            sys.exit(1)

    except ConfigError:
        show_error_banner(
            "Configuração não encontrada",
            "Execute 'prfi init' primeiro para configurar o projeto"
        )
        sys.exit(1)
    except Exception as e:
        show_error_banner(
            "Erro no Deploy",
            str(e)
        )
        sys.exit(1)

def execute_deploy(config: dict, network: str, verify: bool, dry_run: bool, gas_limit: int, gas_price: str) -> bool:
    """Executar deploy do smart contract"""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:

        # Etapa 1: Validar ambiente
        task1 = progress.add_task("🔍 Validando ambiente...", total=100)

        if not validate_environment():
            progress.update(task1, description="❌ Ambiente inválido")
            return False

        progress.update(task1, completed=100, description="✅ Ambiente validado")

        # Etapa 2: Preparar deploy
        task2 = progress.add_task("⚙️ Preparando deploy...", total=100)

        deploy_config = prepare_deploy_config(config, network, gas_limit, gas_price)
        if not deploy_config:
            progress.update(task2, description="❌ Falha na preparação")
            return False

        progress.update(task2, completed=100, description="✅ Deploy preparado")

        # Etapa 3: Executar deploy
        task3 = progress.add_task("🚀 Executando deploy...", total=100)

        if dry_run:
            progress.update(task3, completed=100, description="🧪 Deploy simulado")
            show_deploy_simulation(deploy_config)
            return True

        contract_address = execute_hardhat_deploy(network, progress, task3)
        if not contract_address:
            progress.update(task3, description="❌ Deploy falhou")
            return False

        progress.update(task3, completed=100, description="✅ Deploy executado")

        # Etapa 4: Verificar contrato (se solicitado)
        if verify:
            task4 = progress.add_task("🔍 Verificando contrato...", total=100)

            verification_success = verify_contract(contract_address, network)
            if verification_success:
                progress.update(task4, completed=100, description="✅ Contrato verificado")
            else:
                progress.update(task4, completed=100, description="⚠️ Verificação falhou")

        # Etapa 5: Salvar informações
        task5 = progress.add_task("💾 Salvando informações...", total=100)

        save_deploy_info(contract_address, network, config)
        progress.update(task5, completed=100, description="✅ Informações salvas")

    # Mostrar resumo do deploy
    show_deploy_summary(contract_address, network, verify)

    return True

def validate_environment() -> bool:
    """Validar ambiente de deploy"""

    # Verificar se Node.js está instalado
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print("❌ [red]Node.js não encontrado. Instale Node.js primeiro.[/red]")
        return False

    # Verificar se Hardhat está instalado
    try:
        subprocess.run(["npx", "hardhat", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print("❌ [red]Hardhat não encontrado. Execute 'npm install' primeiro.[/red]")
        return False

    # Verificar se arquivo .env existe
    env_file = Path.cwd() / ".env"
    if not env_file.exists():
        console.print("❌ [red]Arquivo .env não encontrado.[/red]")
        return False

    return True

def prepare_deploy_config(config: dict, network: str, gas_limit: int, gas_price: str) -> dict:
    """Preparar configuração de deploy"""

    deploy_config = {
        "network": network,
        "contract_name": "PRFIC",
        "treasury_address": config.get("blockchain", {}).get("treasury_address"),
        "gas_limit": gas_limit,
        "gas_price": gas_price
    }

    # Validar treasury address
    if not deploy_config["treasury_address"]:
        console.print("❌ [red]Treasury address não configurado[/red]")
        return None

    return deploy_config

def execute_hardhat_deploy(network: str, progress, task_id) -> str:
    """Executar deploy usando Hardhat"""

    try:
        # Navegar para diretório raiz do projeto
        project_root = find_project_root()
        if not project_root:
            console.print("❌ [red]Diretório do projeto não encontrado[/red]")
            return None

        # Executar comando de deploy
        cmd = ["npx", "hardhat", "run", "scripts/deploy.js", "--network", network]

        progress.update(task_id, completed=50, description="🚀 Executando Hardhat...")

        result = subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos timeout
        )

        if result.returncode != 0:
            console.print(f"❌ [red]Erro no deploy:[/red]")
            console.print(result.stderr)
            return None

        # Extrair endereço do contrato do output
        contract_address = extract_contract_address(result.stdout)

        if contract_address:
            console.print(f"✅ [green]Contrato deployado: {contract_address}[/green]")
            return contract_address
        else:
            console.print("❌ [red]Não foi possível extrair endereço do contrato[/red]")
            return None

    except subprocess.TimeoutExpired:
        console.print("❌ [red]Deploy timeout (5 minutos)[/red]")
        return None
    except Exception as e:
        console.print(f"❌ [red]Erro no deploy: {e}[/red]")
        return None

def find_project_root() -> Path:
    """Encontrar diretório raiz do projeto"""

    current = Path.cwd()

    # Procurar por hardhat.config.js
    while current != current.parent:
        if (current / "hardhat.config.js").exists():
            return current
        current = current.parent

    # Se não encontrar, assumir diretório pai do CLI
    cli_dir = Path(__file__).parent.parent.parent
    project_root = cli_dir.parent

    if (project_root / "hardhat.config.js").exists():
        return project_root

    return None

def extract_contract_address(output: str) -> str:
    """Extrair endereço do contrato do output do Hardhat"""

    lines = output.split('\n')
    for line in lines:
        if "PRFIC deployed to:" in line or "Contract deployed to:" in line:
            # Extrair endereço (formato: 0x...)
            parts = line.split()
            for part in parts:
                if part.startswith("0x") and len(part) == 42:
                    return part

    return None

def verify_contract(contract_address: str, network: str) -> bool:
    """Verificar contrato no explorer"""

    try:
        project_root = find_project_root()
        if not project_root:
            return False

        cmd = [
            "npx", "hardhat", "verify",
            "--network", network,
            contract_address
        ]

        result = subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=120  # 2 minutos timeout
        )

        if result.returncode == 0:
            console.print("✅ [green]Contrato verificado com sucesso[/green]")
            return True
        else:
            console.print(f"⚠️ [yellow]Falha na verificação: {result.stderr}[/yellow]")
            return False

    except Exception as e:
        console.print(f"⚠️ [yellow]Erro na verificação: {e}[/yellow]")
        return False

def save_deploy_info(contract_address: str, network: str, config: dict):
    """Salvar informações do deploy"""

    deploy_info = {
        "contract_address": contract_address,
        "network": network,
        "deployed_at": time.time(),
        "explorer_url": get_explorer_url(contract_address, network)
    }

    # Salvar em arquivo JSON
    deploy_file = Path.cwd() / "deploy_info.json"
    with open(deploy_file, "w") as f:
        json.dump(deploy_info, f, indent=2)

    # Atualizar .env se existir
    update_env_file(contract_address)

def get_explorer_url(contract_address: str, network: str) -> str:
    """Obter URL do explorer para o contrato"""

    explorers = {
        "bsc-testnet": f"https://testnet.bscscan.com/address/{contract_address}",
        "bsc-mainnet": f"https://bscscan.com/address/{contract_address}",
        "polygon-mumbai": f"https://mumbai.polygonscan.com/address/{contract_address}",
        "polygon-mainnet": f"https://polygonscan.com/address/{contract_address}"
    }

    return explorers.get(network, f"https://etherscan.io/address/{contract_address}")

def update_env_file(contract_address: str):
    """Atualizar arquivo .env com endereço do contrato"""

    env_file = Path.cwd() / ".env"
    if not env_file.exists():
        return

    # Ler arquivo atual
    with open(env_file, "r") as f:
        lines = f.readlines()

    # Atualizar ou adicionar PRFIC_CONTRACT_ADDRESS
    updated = False
    for i, line in enumerate(lines):
        if line.startswith("PRFIC_CONTRACT_ADDRESS="):
            lines[i] = f"PRFIC_CONTRACT_ADDRESS={contract_address}\n"
            updated = True
            break

    if not updated:
        lines.append(f"PRFIC_CONTRACT_ADDRESS={contract_address}\n")

    # Salvar arquivo
    with open(env_file, "w") as f:
        f.writelines(lines)

def show_deploy_simulation(deploy_config: dict):
    """Mostrar simulação do deploy"""

    table = Table(title="🧪 Simulação de Deploy")
    table.add_column("Parâmetro", style="cyan")
    table.add_column("Valor", style="green")

    table.add_row("Rede", deploy_config["network"])
    table.add_row("Contrato", deploy_config["contract_name"])
    table.add_row("Treasury", deploy_config["treasury_address"])

    if deploy_config["gas_limit"]:
        table.add_row("Gas Limit", str(deploy_config["gas_limit"]))

    if deploy_config["gas_price"]:
        table.add_row("Gas Price", f"{deploy_config['gas_price']} gwei")

    console.print(table)

def show_deploy_summary(contract_address: str, network: str, verified: bool):
    """Mostrar resumo do deploy"""

    summary_text = Text()
    summary_text.append("🎉 Deploy Concluído com Sucesso!\n\n", style="bold green")

    summary_text.append("📋 Informações do Deploy:\n", style="bold")
    summary_text.append(f"• Contrato: {contract_address}\n", style="dim")
    summary_text.append(f"• Rede: {network}\n", style="dim")
    summary_text.append(f"• Verificado: {'✅ Sim' if verified else '❌ Não'}\n", style="dim")
    summary_text.append(f"• Explorer: {get_explorer_url(contract_address, network)}\n", style="dim")

    summary_text.append("\n🎯 Próximos Passos:\n", style="bold yellow")
    summary_text.append("1. prfi test --blockchain    # Testar conexão\n", style="dim")
    summary_text.append("2. prfi dashboard           # Monitorar sistema\n", style="dim")
    summary_text.append("3. Integrar com suas APIs   # Começar a usar\n", style="dim")

    console.print(Panel(
        summary_text,
        title="✅ Deploy Concluído",
        border_style="green"
    ))
