#!/usr/bin/env python3
"""
PRFI CLI 2.0 - Init Command
Setup wizard interativo e intuitivo
"""

import click
import inquirer
import os
import json
import yaml
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich import box
import time

from ..utils.config import save_config, get_config_path
from ..utils.templates import get_available_templates, load_template
from ..utils.validation import validate_config
from ..utils.crypto import generate_keypair
from ..utils.console import create_console, safe_print
from ..templates.presets import PRESET_CONFIGS

console = create_console()

@click.command()
@click.option('--quick', is_flag=True, help='Setup rápido com configurações padrão')
@click.option('--template', help='Usar template específico')
@click.option('--output', '-o', help='Arquivo de saída da configuração')
def init(quick, template, output):
    """🎯 Setup inicial interativo do PRFI Protocol"""
    
    safe_print(console, "[*] [bold blue]PRFI Protocol - Setup Inicial[/bold blue]")
    safe_print(console, "Vamos configurar seu projeto PRFI de forma simples e rapida!\n")
    
    if quick:
        return quick_setup(output)
    
    if template:
        return template_setup(template, output)
    
    return interactive_setup(output)

def quick_setup(output_file=None):
    """Setup rápido com configurações padrão"""
    console.print("🚀 [bold green]Setup Rápido[/bold green]")
    console.print("Usando configurações padrão otimizadas...\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        # Gerar configuração padrão
        task1 = progress.add_task("Gerando configuração...", total=None)
        time.sleep(1)
        
        config = {
            "project": {
                "name": "meu-projeto-prfi",
                "description": "Projeto PRFI gerado automaticamente",
                "version": "1.0.0"
            },
            "prfi": PRESET_CONFIGS["balanced"],
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
        progress.update(task1, description="✅ Configuração gerada")
        
        # Gerar chaves
        task2 = progress.add_task("Gerando chaves criptográficas...", total=None)
        time.sleep(0.5)
        
        private_key, public_key = generate_keypair()
        config["security"] = {
            "private_key": private_key,
            "public_key": public_key
        }
        progress.update(task2, description="✅ Chaves geradas")
        
        # Salvar configuração
        task3 = progress.add_task("Salvando configuração...", total=None)
        time.sleep(0.5)
        
        config_path = save_config(config, output_file)
        progress.update(task3, description="✅ Configuração salva")
    
    console.print(f"\n✅ [bold green]Setup concluído![/bold green]")
    console.print(f"📁 Configuração salva em: {config_path}")
    console.print("\n🎯 [bold]Próximos passos:[/bold]")
    console.print("1. prfi test          # Testar configuração")
    console.print("2. prfi deploy        # Deploy do smart contract")
    console.print("3. prfi dashboard     # Abrir interface web")

def template_setup(template_name, output_file=None):
    """Setup usando template específico"""
    console.print(f"📋 [bold blue]Setup com Template: {template_name}[/bold blue]\n")
    
    try:
        template = load_template(template_name)
        
        # Personalizar template
        config = customize_template(template)
        
        # Salvar
        config_path = save_config(config, output_file)
        
        console.print(f"\n✅ [bold green]Template aplicado com sucesso![/bold green]")
        console.print(f"📁 Configuração salva em: {config_path}")
        
    except Exception as e:
        console.print(f"❌ [red]Erro ao carregar template: {e}[/red]")
        return False

def interactive_setup(output_file=None):
    """Setup interativo completo"""
    console.print("🎯 [bold blue]Setup Interativo[/bold blue]")
    console.print("Vamos configurar seu projeto passo a passo!\n")
    
    config = {}
    
    # 1. Informações do projeto
    config["project"] = collect_project_info()
    
    # 2. Escolher template ou configuração customizada
    use_template = Confirm.ask("Deseja usar um template pré-configurado?", default=True)
    
    if use_template:
        template_name = choose_template()
        template = load_template(template_name)
        config.update(template)
        config = customize_template(config)
    else:
        # 3. Configuração customizada
        config["prfi"] = collect_prfi_config()
        config["blockchain"] = collect_blockchain_config()
        config["apis"] = collect_apis_config()
    
    # 4. Configurações de segurança
    config["security"] = collect_security_config()
    
    # 5. Monitoramento
    config["monitoring"] = collect_monitoring_config()
    
    # 6. Validar configuração
    console.print("\n🔍 [bold yellow]Validando configuração...[/bold yellow]")
    
    validation_result = validate_config(config)
    if not validation_result.valid:
        console.print("❌ [red]Configuração inválida:[/red]")
        for error in validation_result.errors:
            console.print(f"  • {error}")
        return False
    
    # 7. Salvar
    config_path = save_config(config, output_file)
    
    # 8. Resumo final
    show_setup_summary(config, config_path)
    
    return True

def collect_project_info():
    """Coletar informações básicas do projeto"""
    console.print("📋 [bold]Informações do Projeto[/bold]\n")
    
    name = Prompt.ask("Nome do projeto", default="meu-projeto-prfi")
    description = Prompt.ask("Descrição", default="Projeto PRFI para APIs resilientes")
    version = Prompt.ask("Versão", default="1.0.0")
    
    return {
        "name": name,
        "description": description,
        "version": version
    }

def choose_template():
    """Escolher template"""
    templates = get_available_templates()
    
    questions = [
        inquirer.List(
            'template',
            message="Escolha um template",
            choices=[(t["name"], t["id"]) for t in templates],
        ),
    ]
    
    answers = inquirer.prompt(questions)
    return answers['template']

def customize_template(config):
    """Personalizar configurações do template"""
    console.print("\n⚙️ [bold]Personalizando Template[/bold]\n")
    
    # Personalizar rede blockchain
    if "blockchain" in config:
        network = inquirer.list_input(
            "Rede blockchain",
            choices=[
                ("BSC Testnet (recomendado)", "bsc-testnet"),
                ("BSC Mainnet", "bsc-mainnet"),
                ("Polygon Mumbai", "polygon-mumbai"),
                ("Polygon Mainnet", "polygon-mainnet"),
            ],
            default=config["blockchain"].get("network", "bsc-testnet")
        )
        config["blockchain"]["network"] = network
    
    # Personalizar porta do dashboard
    if "monitoring" in config:
        port = Prompt.ask(
            "Porta do dashboard",
            default=str(config["monitoring"].get("dashboard_port", 8080))
        )
        config["monitoring"]["dashboard_port"] = int(port)
    
    return config

def collect_prfi_config():
    """Coletar configurações PRFI"""
    console.print("🔄 [bold]Configurações PRFI[/bold]\n")
    
    preset = inquirer.list_input(
        "Escolha um preset de configuração",
        choices=[
            ("Balanceado (recomendado)", "balanced"),
            ("Agressivo (mais tentativas)", "aggressive"),
            ("Conservador (menos tentativas)", "conservative"),
            ("Customizado", "custom")
        ]
    )
    
    if preset == "custom":
        return collect_custom_prfi_config()
    else:
        return PRESET_CONFIGS[preset]

def collect_custom_prfi_config():
    """Coletar configuração PRFI customizada"""
    max_retries = int(Prompt.ask("Máximo de tentativas", default="5"))
    initial_delay = float(Prompt.ask("Delay inicial (segundos)", default="1.0"))
    max_delay = float(Prompt.ask("Delay máximo (segundos)", default="300.0"))
    
    return {
        "retry": {
            "max_attempts": max_retries,
            "initial_delay": initial_delay,
            "max_delay": max_delay,
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
    }

def collect_blockchain_config():
    """Coletar configurações blockchain"""
    console.print("⛓️ [bold]Configurações Blockchain[/bold]\n")
    
    network = inquirer.list_input(
        "Rede blockchain",
        choices=[
            ("BSC Testnet (recomendado para testes)", "bsc-testnet"),
            ("BSC Mainnet (produção)", "bsc-mainnet"),
            ("Polygon Mumbai (testnet)", "polygon-mumbai"),
            ("Polygon Mainnet (produção)", "polygon-mainnet"),
        ]
    )
    
    auto_deploy = Confirm.ask("Deploy automático do smart contract?", default=True)
    
    return {
        "network": network,
        "auto_deploy": auto_deploy
    }

def collect_apis_config():
    """Coletar configurações de APIs"""
    console.print("🌐 [bold]Configurações de APIs[/bold]\n")
    
    apis = []
    
    add_api = Confirm.ask("Deseja adicionar uma API agora?", default=False)
    
    while add_api:
        api_url = Prompt.ask("URL da API")
        api_name = Prompt.ask("Nome da API", default=api_url.split("//")[1].split("/")[0])
        
        apis.append({
            "name": api_name,
            "url": api_url,
            "method": "GET",
            "enabled": True
        })
        
        add_api = Confirm.ask("Adicionar outra API?", default=False)
    
    return apis

def collect_security_config():
    """Coletar configurações de segurança"""
    console.print("🔐 [bold]Configurações de Segurança[/bold]\n")
    
    # Gerar chaves automaticamente
    private_key, public_key = generate_keypair()
    
    console.print("✅ Chaves criptográficas geradas automaticamente")
    
    return {
        "private_key": private_key,
        "public_key": public_key,
        "enable_signature_validation": True,
        "require_https": True
    }

def collect_monitoring_config():
    """Coletar configurações de monitoramento"""
    console.print("📊 [bold]Configurações de Monitoramento[/bold]\n")
    
    enabled = Confirm.ask("Habilitar monitoramento?", default=True)
    
    if not enabled:
        return {"enabled": False}
    
    port = int(Prompt.ask("Porta do dashboard", default="8080"))
    
    return {
        "enabled": True,
        "dashboard_port": port,
        "metrics_enabled": True,
        "health_checks": True
    }

def show_setup_summary(config, config_path):
    """Mostrar resumo do setup"""
    console.print("\n🎉 [bold green]Setup Concluído com Sucesso![/bold green]\n")
    
    summary = Text()
    summary.append("📋 Resumo da Configuração:\n\n", style="bold")
    summary.append(f"• Projeto: {config['project']['name']}\n")
    summary.append(f"• Rede: {config.get('blockchain', {}).get('network', 'N/A')}\n")
    summary.append(f"• APIs configuradas: {len(config.get('apis', []))}\n")
    summary.append(f"• Monitoramento: {'✅' if config.get('monitoring', {}).get('enabled') else '❌'}\n")
    summary.append(f"• Arquivo: {config_path}\n\n")
    
    summary.append("🎯 Próximos Passos:\n", style="bold yellow")
    summary.append("1. prfi test          # Testar configuração\n")
    summary.append("2. prfi deploy        # Deploy do smart contract\n")
    summary.append("3. prfi dashboard     # Abrir interface web\n")
    
    console.print(Panel(
        summary,
        title="✅ Setup Concluído",
        border_style="green",
        box=box.ROUNDED
    ))
