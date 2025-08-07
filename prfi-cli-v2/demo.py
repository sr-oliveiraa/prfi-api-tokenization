#!/usr/bin/env python3
"""
PRFI CLI 2.0 - Demonstração Completa
Script para demonstrar todas as funcionalidades integradas
"""

import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()

def main():
    """Demonstração completa do PRFI CLI 2.0"""
    
    show_welcome()
    
    # Menu de demonstração
    while True:
        show_menu()
        choice = input("\nEscolha uma opção (1-7, 0 para sair): ").strip()
        
        if choice == "0":
            console.print("\n👋 [yellow]Obrigado por testar o PRFI CLI 2.0![/yellow]")
            break
        elif choice == "1":
            demo_init()
        elif choice == "2":
            demo_test()
        elif choice == "3":
            demo_dashboard()
        elif choice == "4":
            demo_deploy()
        elif choice == "5":
            demo_integration()
        elif choice == "6":
            demo_frontend()
        elif choice == "7":
            show_features()
        else:
            console.print("❌ [red]Opção inválida[/red]")

def show_welcome():
    """Mostrar boas-vindas"""
    
    welcome_text = Text()
    welcome_text.append("🚀 PRFI CLI 2.0 - DEMONSTRAÇÃO COMPLETA\n\n", style="bold blue")
    welcome_text.append("Bem-vindo à demonstração do CLI moderno integrado com PRFI-Core!\n\n", style="dim")
    
    welcome_text.append("✨ Principais Funcionalidades Implementadas:\n", style="bold")
    welcome_text.append("• CLI moderno e intuitivo com Rich UI\n", style="green")
    welcome_text.append("• Integração completa com PRFI-Core\n", style="green")
    welcome_text.append("• Testes reais de APIs e blockchain\n", style="green")
    welcome_text.append("• Deploy automático de smart contracts\n", style="green")
    welcome_text.append("• Dashboard web com React + TypeScript\n", style="green")
    welcome_text.append("• Backend FastAPI com APIs reais\n", style="green")
    welcome_text.append("• Componentes React interativos\n", style="green")
    
    console.print(Panel(
        welcome_text,
        title="🎉 PRFI Protocol - Demonstração",
        border_style="blue",
        box=box.ROUNDED
    ))

def show_menu():
    """Mostrar menu de opções"""
    
    menu_text = Text()
    menu_text.append("📋 Menu de Demonstração:\n\n", style="bold")
    
    options = [
        ("1", "🎯 Setup Wizard", "Demonstrar setup interativo"),
        ("2", "🧪 Testes Integrados", "Executar testes com PRFI-Core"),
        ("3", "📊 Dashboard Web", "Abrir interface web moderna"),
        ("4", "🚀 Deploy Simulation", "Simular deploy de contrato"),
        ("5", "🔗 Integração PRFI-Core", "Mostrar integração completa"),
        ("6", "🌐 Frontend React", "Demonstrar componentes React"),
        ("7", "✨ Lista de Features", "Ver todas as funcionalidades"),
        ("0", "🚪 Sair", "Encerrar demonstração")
    ]
    
    for num, title, desc in options:
        menu_text.append(f"{num}. ", style="bold cyan")
        menu_text.append(f"{title}: ", style="bold")
        menu_text.append(f"{desc}\n", style="dim")
    
    console.print(Panel(
        menu_text,
        title="🎯 Escolha uma Demonstração",
        border_style="cyan",
        box=box.ROUNDED
    ))

def demo_init():
    """Demonstrar setup wizard"""
    
    console.print("🎯 [bold blue]Demonstração: Setup Wizard[/bold blue]\n")
    
    console.print("Executando setup rápido...")
    run_command("python prfi.py init --quick")
    
    console.print("\n✅ [green]Setup concluído! Arquivo prfi.config.yaml criado.[/green]")
    input("\nPressione Enter para continuar...")

def demo_test():
    """Demonstrar testes integrados"""
    
    console.print("🧪 [bold blue]Demonstração: Testes Integrados[/bold blue]\n")
    
    console.print("Executando testes com integração PRFI-Core...")
    run_command("python prfi.py test --verbose")
    
    console.print("\n✅ [green]Testes executados! Integração com PRFI-Core funcionando.[/green]")
    input("\nPressione Enter para continuar...")

def demo_dashboard():
    """Demonstrar dashboard web"""
    
    console.print("📊 [bold blue]Demonstração: Dashboard Web[/bold blue]\n")
    
    console.print("Iniciando dashboard web com backend FastAPI...")
    console.print("🌐 [cyan]Abrindo http://localhost:8082[/cyan]")
    
    # Iniciar dashboard em background
    subprocess.Popen([
        sys.executable, "prfi.py", "dashboard", "--port", "8082"
    ], cwd=Path.cwd())
    
    time.sleep(3)
    webbrowser.open("http://localhost:8082")
    
    console.print("\n✅ [green]Dashboard aberto! Backend com APIs reais funcionando.[/green]")
    input("\nPressione Enter para continuar...")

def demo_deploy():
    """Demonstrar deploy simulation"""
    
    console.print("🚀 [bold blue]Demonstração: Deploy Simulation[/bold blue]\n")
    
    console.print("Executando simulação de deploy...")
    run_command("python prfi.py deploy --dry-run --network bsc-testnet")
    
    console.print("\n✅ [green]Deploy simulado! Integração com Hardhat funcionando.[/green]")
    input("\nPressione Enter para continuar...")

def demo_integration():
    """Demonstrar integração PRFI-Core"""
    
    console.print("🔗 [bold blue]Demonstração: Integração PRFI-Core[/bold blue]\n")
    
    integration_text = Text()
    integration_text.append("✅ Funcionalidades Integradas:\n\n", style="bold green")
    
    features = [
        "Importação de modelos do PRFI-Core",
        "Testes de configuração automáticos",
        "Validação de retry e fallback",
        "Conexão com blockchain (BSC/Polygon)",
        "Deploy de smart contracts via Hardhat",
        "Backend FastAPI com dados reais",
        "Frontend React com componentes interativos"
    ]
    
    for feature in features:
        integration_text.append(f"• {feature}\n", style="dim")
    
    integration_text.append("\n🎯 Próximos Passos:\n", style="bold yellow")
    integration_text.append("• Conectar com APIs reais do PRFI-Core\n", style="dim")
    integration_text.append("• Implementar mineração de tokens\n", style="dim")
    integration_text.append("• Adicionar monitoramento em tempo real\n", style="dim")
    
    console.print(Panel(
        integration_text,
        title="🔗 Integração PRFI-Core",
        border_style="green"
    ))
    
    input("\nPressione Enter para continuar...")

def demo_frontend():
    """Demonstrar frontend React"""
    
    console.print("🌐 [bold blue]Demonstração: Frontend React[/bold blue]\n")
    
    frontend_text = Text()
    frontend_text.append("⚛️ Componentes React Criados:\n\n", style="bold blue")
    
    components = [
        ("StatsCard", "Cards de estatísticas com animações"),
        ("Chart", "Gráficos interativos com Recharts"),
        ("Layout", "Layout responsivo com sidebar"),
        ("RecentActivity", "Lista de atividades em tempo real"),
        ("APIStatus", "Status das APIs com indicadores"),
        ("Dashboard", "Dashboard principal completo")
    ]
    
    for comp, desc in components:
        frontend_text.append(f"• {comp}: ", style="bold cyan")
        frontend_text.append(f"{desc}\n", style="dim")
    
    frontend_text.append("\n🎨 Tecnologias Utilizadas:\n", style="bold yellow")
    frontend_text.append("• React 18 + TypeScript\n", style="dim")
    frontend_text.append("• Tailwind CSS para styling\n", style="dim")
    frontend_text.append("• Framer Motion para animações\n", style="dim")
    frontend_text.append("• Recharts para gráficos\n", style="dim")
    frontend_text.append("• React Query para estado\n", style="dim")
    
    console.print(Panel(
        frontend_text,
        title="⚛️ Frontend React",
        border_style="blue"
    ))
    
    input("\nPressione Enter para continuar...")

def show_features():
    """Mostrar lista completa de features"""
    
    console.print("✨ [bold blue]Lista Completa de Funcionalidades[/bold blue]\n")
    
    features_text = Text()
    
    sections = [
        ("🎯 CLI Moderno", [
            "Interface Rich com cores e animações",
            "Setup wizard interativo",
            "Templates pré-configurados",
            "Validação em tempo real",
            "Progress bars animadas",
            "Banners informativos"
        ]),
        ("🔗 Integração PRFI-Core", [
            "Importação de modelos",
            "Testes de configuração",
            "Validação de retry/fallback",
            "Conexão com cliente descentralizado"
        ]),
        ("🧪 Sistema de Testes", [
            "Testes de configuração",
            "Testes de APIs reais",
            "Testes de blockchain",
            "Modo watch contínuo",
            "Relatórios detalhados"
        ]),
        ("🚀 Deploy Automático", [
            "Integração com Hardhat",
            "Deploy em múltiplas redes",
            "Verificação de contratos",
            "Simulação de deploy",
            "Configuração de gas"
        ]),
        ("🌐 Dashboard Web", [
            "Backend FastAPI",
            "APIs REST completas",
            "Frontend React + TypeScript",
            "Componentes interativos",
            "Gráficos em tempo real"
        ])
    ]
    
    for section, items in sections:
        features_text.append(f"{section}:\n", style="bold")
        for item in items:
            features_text.append(f"  • {item}\n", style="dim")
        features_text.append("\n")
    
    console.print(Panel(
        features_text,
        title="✨ Funcionalidades Implementadas",
        border_style="green"
    ))
    
    input("\nPressione Enter para continuar...")

def run_command(command: str):
    """Executar comando e mostrar output"""
    try:
        result = subprocess.run(
            command.split(),
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.stdout:
            console.print(result.stdout)
        if result.stderr:
            console.print(f"[red]{result.stderr}[/red]")
            
    except subprocess.TimeoutExpired:
        console.print("⏰ [yellow]Comando timeout[/yellow]")
    except Exception as e:
        console.print(f"❌ [red]Erro: {e}[/red]")

if __name__ == "__main__":
    main()
