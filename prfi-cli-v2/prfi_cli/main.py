#!/usr/bin/env python3
"""
PRFI CLI 2.0 - Main Entry Point
CLI moderno e intuitivo para PRFI Protocol
"""

import click
import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
import sys
import os

from .commands import init, deploy, test, dashboard, config, monitor
from .utils.banner import show_banner
from .utils.config import load_config, ConfigError
from .utils.logger import setup_logger

console = Console()
logger = setup_logger()

@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Mostrar versão')
@click.option('--config', '-c', help='Arquivo de configuração customizado')
@click.pass_context
def cli(ctx, version, config):
    """
    🚀 PRFI CLI 2.0 - Interface moderna para PRFI Protocol
    
    Gerencie APIs resilientes com retry, fallback e tokenização blockchain
    de forma simples e intuitiva.
    """
    ctx.ensure_object(dict)
    ctx.obj['config_file'] = config
    
    if version:
        show_version()
        return
    
    if ctx.invoked_subcommand is None:
        show_banner()
        show_help()

def show_version():
    """Mostrar informações de versão"""
    version_text = Text()
    version_text.append("PRFI CLI ", style="bold blue")
    version_text.append("v2.0.0", style="bold green")
    version_text.append("\n🚀 Interface moderna para PRFI Protocol", style="dim")
    
    console.print(Panel(
        version_text,
        title="Versão",
        border_style="blue",
        box=box.ROUNDED
    ))

def show_help():
    """Mostrar ajuda principal com comandos disponíveis"""
    help_text = Text()
    help_text.append("Comandos Principais:\n\n", style="bold")
    
    commands = [
        ("🎯 prfi init", "Setup inicial interativo", "green"),
        ("🚀 prfi deploy", "Deploy do smart contract", "blue"),
        ("🧪 prfi test", "Testar configuração e APIs", "yellow"),
        ("📊 prfi dashboard", "Abrir dashboard web", "magenta"),
        ("⚙️  prfi config", "Gerenciar configurações", "cyan"),
        ("📈 prfi monitor", "Monitorar em tempo real", "red"),
    ]
    
    for cmd, desc, color in commands:
        help_text.append(f"{cmd:<20}", style=f"bold {color}")
        help_text.append(f"{desc}\n", style="dim")
    
    help_text.append("\n💡 ", style="yellow")
    help_text.append("Dica: Use 'prfi init' para começar!", style="bold")
    
    console.print(Panel(
        help_text,
        title="🚀 PRFI Protocol CLI",
        subtitle="Use --help em qualquer comando para mais detalhes",
        border_style="blue",
        box=box.ROUNDED
    ))

# Registrar comandos
cli.add_command(init.init)
cli.add_command(deploy.deploy)
cli.add_command(test.test)
cli.add_command(dashboard.dashboard)
cli.add_command(config.config)
cli.add_command(monitor.monitor)

# Comandos de conveniência
@cli.command()
def quickstart():
    """🚀 Setup rápido para começar imediatamente"""
    console.print("🚀 [bold blue]PRFI Quickstart[/bold blue]")
    console.print("Iniciando setup rápido...\n")
    
    # Executar init em modo rápido
    ctx = click.get_current_context()
    ctx.invoke(init.init, quick=True)

@cli.command()
@click.option('--open', '-o', is_flag=True, help='Abrir dashboard automaticamente')
def start(open):
    """🎯 Iniciar PRFI Protocol (all-in-one)"""
    console.print("🎯 [bold green]Iniciando PRFI Protocol...[/bold green]\n")
    
    try:
        # Verificar se está configurado
        config_data = load_config()
        
        # Iniciar dashboard se solicitado
        if open:
            ctx = click.get_current_context()
            ctx.invoke(dashboard.dashboard, port=8080, open_browser=True)
        else:
            console.print("✅ PRFI Protocol está pronto!")
            console.print("💡 Use 'prfi dashboard' para abrir a interface web")
            
    except ConfigError:
        console.print("❌ [red]PRFI não está configurado[/red]")
        console.print("💡 Execute 'prfi init' primeiro")
        sys.exit(1)

@cli.command()
def status():
    """📊 Mostrar status atual do PRFI"""
    from .utils.status import show_status
    show_status()

@cli.command()
def doctor():
    """🩺 Diagnosticar problemas comuns"""
    from .utils.doctor import run_diagnostics
    run_diagnostics()

def main():
    """Entry point principal"""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n👋 [yellow]Operação cancelada pelo usuário[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n❌ [red]Erro inesperado: {e}[/red]")
        logger.error(f"Erro CLI: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
