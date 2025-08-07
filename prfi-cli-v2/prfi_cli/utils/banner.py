#!/usr/bin/env python3
"""
PRFI CLI 2.0 - Banner Utils
Banner e arte ASCII para o CLI
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box
import random

console = Console()

def show_banner():
    """Mostrar banner principal do PRFI CLI"""
    
    # Arte ASCII do PRFI
    ascii_art = """
    ██████╗ ██████╗ ███████╗██╗
    ██╔══██╗██╔══██╗██╔════╝██║
    ██████╔╝██████╔╝█████╗  ██║
    ██╔═══╝ ██╔══██╗██╔══╝  ██║
    ██║     ██║  ██║██║     ██║
    ╚═╝     ╚═╝  ╚═╝╚═╝     ╚═╝
    """
    
    # Criar texto do banner
    banner_text = Text()
    banner_text.append(ascii_art, style="bold blue")
    banner_text.append("\n")
    banner_text.append("Protocol for Resilient & Fallback Integrations", style="bold")
    banner_text.append("\n")
    banner_text.append("v2.0.0", style="dim")
    banner_text.append(" • ", style="dim")
    banner_text.append("CLI Moderno e Intuitivo", style="dim")
    
    # Mostrar banner centralizado
    console.print(Panel(
        Align.center(banner_text),
        border_style="blue",
        box=box.ROUNDED,
        padding=(1, 2)
    ))

def show_welcome_message():
    """Mostrar mensagem de boas-vindas"""
    
    messages = [
        "🚀 Bem-vindo ao futuro das integrações de API!",
        "⚡ Transforme suas APIs em sistemas resilientes!",
        "🎯 Retry, Fallback e Tokenização em um só lugar!",
        "🌟 Construa APIs que nunca falham!",
        "💎 Ganhe tokens enquanto suas APIs funcionam!"
    ]
    
    message = random.choice(messages)
    
    welcome_text = Text()
    welcome_text.append(message, style="bold green")
    welcome_text.append("\n\n")
    welcome_text.append("O PRFI Protocol torna suas integrações de API mais robustas ", style="dim")
    welcome_text.append("com retry automático, fallback inteligente e tokenização blockchain.", style="dim")
    
    console.print(Panel(
        welcome_text,
        title="✨ Bem-vindo",
        border_style="green",
        box=box.ROUNDED
    ))

def show_success_banner(title: str, message: str = ""):
    """Mostrar banner de sucesso"""
    
    success_text = Text()
    success_text.append("✅ ", style="bold green")
    success_text.append(title, style="bold green")
    
    if message:
        success_text.append(f"\n\n{message}", style="dim")
    
    console.print(Panel(
        success_text,
        border_style="green",
        box=box.ROUNDED
    ))

def show_error_banner(title: str, message: str = ""):
    """Mostrar banner de erro"""
    
    error_text = Text()
    error_text.append("❌ ", style="bold red")
    error_text.append(title, style="bold red")
    
    if message:
        error_text.append(f"\n\n{message}", style="dim")
    
    console.print(Panel(
        error_text,
        border_style="red",
        box=box.ROUNDED
    ))

def show_warning_banner(title: str, message: str = ""):
    """Mostrar banner de aviso"""
    
    warning_text = Text()
    warning_text.append("⚠️ ", style="bold yellow")
    warning_text.append(title, style="bold yellow")
    
    if message:
        warning_text.append(f"\n\n{message}", style="dim")
    
    console.print(Panel(
        warning_text,
        border_style="yellow",
        box=box.ROUNDED
    ))

def show_info_banner(title: str, message: str = ""):
    """Mostrar banner informativo"""
    
    info_text = Text()
    info_text.append("ℹ️ ", style="bold blue")
    info_text.append(title, style="bold blue")
    
    if message:
        info_text.append(f"\n\n{message}", style="dim")
    
    console.print(Panel(
        info_text,
        border_style="blue",
        box=box.ROUNDED
    ))

def show_progress_banner(title: str, steps: list):
    """Mostrar banner de progresso com steps"""
    
    progress_text = Text()
    progress_text.append("🚀 ", style="bold blue")
    progress_text.append(title, style="bold blue")
    progress_text.append("\n\n", style="dim")
    
    for i, step in enumerate(steps, 1):
        progress_text.append(f"{i}. ", style="bold")
        progress_text.append(f"{step}\n", style="dim")
    
    console.print(Panel(
        progress_text,
        border_style="blue",
        box=box.ROUNDED
    ))

def show_feature_highlight():
    """Mostrar destaque das funcionalidades"""
    
    features_text = Text()
    features_text.append("🎯 Principais Funcionalidades:\n\n", style="bold")
    
    features = [
        ("🔄", "Retry Automático", "Tentativas inteligentes com backoff exponencial"),
        ("🔀", "Fallback Inteligente", "Endpoints alternativos automáticos"),
        ("⛏️", "Mineração de Tokens", "Ganhe PRFIC tokens por cada evento processado"),
        ("📊", "Dashboard Moderno", "Interface web responsiva e intuitiva"),
        ("🛡️", "Segurança Avançada", "Assinatura digital e validação criptográfica"),
        ("🌐", "Multi-Blockchain", "Suporte para BSC, Polygon e outras redes"),
    ]
    
    for icon, title, desc in features:
        features_text.append(f"{icon} ", style="bold")
        features_text.append(f"{title}: ", style="bold blue")
        features_text.append(f"{desc}\n", style="dim")
    
    console.print(Panel(
        features_text,
        title="✨ Por que usar PRFI?",
        border_style="blue",
        box=box.ROUNDED
    ))

def show_quick_start():
    """Mostrar guia de início rápido"""
    
    quickstart_text = Text()
    quickstart_text.append("🚀 Início Rápido:\n\n", style="bold green")
    
    steps = [
        ("prfi init", "Setup inicial interativo"),
        ("prfi test", "Testar configuração"),
        ("prfi deploy", "Deploy do smart contract"),
        ("prfi dashboard", "Abrir interface web"),
    ]
    
    for cmd, desc in steps:
        quickstart_text.append("$ ", style="dim")
        quickstart_text.append(f"{cmd}", style="bold cyan")
        quickstart_text.append(f"  # {desc}\n", style="dim")
    
    quickstart_text.append("\n💡 ", style="yellow")
    quickstart_text.append("Dica: Use 'prfi --help' para ver todos os comandos!", style="bold")
    
    console.print(Panel(
        quickstart_text,
        title="⚡ Como começar",
        border_style="green",
        box=box.ROUNDED
    ))
