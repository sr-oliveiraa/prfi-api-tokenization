#!/usr/bin/env python3
"""
PRFI CLI 2.0 - Dashboard Command
Interface web moderna e responsiva
"""

import click
import asyncio
import webbrowser
import threading
import time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

from ..web.server import create_app
from ..utils.config import load_config, ConfigError
from ..utils.network import find_free_port, get_local_ip

console = Console()

@click.command()
@click.option('--port', '-p', default=8080, help='Porta do servidor (padrão: 8080)')
@click.option('--host', '-h', default='127.0.0.1', help='Host do servidor (padrão: 127.0.0.1)')
@click.option('--open-browser', '-o', is_flag=True, help='Abrir navegador automaticamente')
@click.option('--dev', is_flag=True, help='Modo desenvolvimento (hot reload)')
@click.option('--public', is_flag=True, help='Permitir acesso externo (0.0.0.0)')
def dashboard(port, host, open_browser, dev, public):
    """📊 Abrir dashboard web do PRFI Protocol"""
    
    console.print("📊 [bold blue]PRFI Dashboard[/bold blue]")
    console.print("Iniciando interface web moderna...\n")
    
    try:
        # Carregar configuração
        config = load_config()
        
        # Ajustar host se público
        if public:
            host = '0.0.0.0'
            console.print("🌐 [yellow]Modo público ativado - acessível externamente[/yellow]")
        
        # Encontrar porta livre se necessário
        if not is_port_free(host, port):
            original_port = port
            port = find_free_port(port)
            console.print(f"⚠️ [yellow]Porta {original_port} ocupada, usando {port}[/yellow]")
        
        # Criar aplicação
        app = create_app(config, dev_mode=dev)
        
        # Mostrar informações de acesso
        show_access_info(host, port, public)
        
        # Abrir navegador se solicitado
        if open_browser:
            url = f"http://{'localhost' if host == '127.0.0.1' else host}:{port}"
            threading.Timer(1.5, lambda: webbrowser.open(url)).start()
        
        # Iniciar servidor
        start_server(app, host, port, dev)
        
    except ConfigError:
        console.print("❌ [red]PRFI não está configurado[/red]")
        console.print("💡 Execute 'prfi init' primeiro")
        return False
    except KeyboardInterrupt:
        console.print("\n👋 [yellow]Dashboard encerrado pelo usuário[/yellow]")
        return True
    except Exception as e:
        console.print(f"❌ [red]Erro ao iniciar dashboard: {e}[/red]")
        return False

def show_access_info(host, port, public):
    """Mostrar informações de acesso ao dashboard"""
    info_text = Text()
    info_text.append("🚀 Dashboard PRFI iniciado com sucesso!\n\n", style="bold green")
    
    # URLs de acesso
    info_text.append("📍 URLs de Acesso:\n", style="bold")
    
    if host == '127.0.0.1':
        info_text.append(f"   Local:    http://localhost:{port}\n", style="cyan")
        info_text.append(f"   IP:       http://127.0.0.1:{port}\n", style="cyan")
    else:
        info_text.append(f"   Local:    http://localhost:{port}\n", style="cyan")
        if public:
            local_ip = get_local_ip()
            info_text.append(f"   Rede:     http://{local_ip}:{port}\n", style="cyan")
            info_text.append(f"   Público:  http://{host}:{port}\n", style="cyan")
    
    info_text.append("\n🎯 Funcionalidades:\n", style="bold")
    info_text.append("   • Dashboard em tempo real\n", style="dim")
    info_text.append("   • Monitoramento de APIs\n", style="dim")
    info_text.append("   • Configuração visual\n", style="dim")
    info_text.append("   • Logs e métricas\n", style="dim")
    info_text.append("   • Gerenciamento de tokens\n", style="dim")
    
    info_text.append("\n⌨️  Controles:\n", style="bold")
    info_text.append("   Ctrl+C para parar o servidor\n", style="yellow")
    
    console.print(Panel(
        info_text,
        title="🌐 PRFI Dashboard Online",
        border_style="green",
        box=box.ROUNDED
    ))

def start_server(app, host, port, dev_mode):
    """Iniciar servidor web"""
    import uvicorn
    
    # Configuração do servidor
    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        reload=dev_mode,
        reload_dirs=["prfi_cli/web"] if dev_mode else None,
        log_level="info" if dev_mode else "warning",
        access_log=dev_mode
    )
    
    server = uvicorn.Server(config)
    
    try:
        # Executar servidor
        asyncio.run(server.serve())
    except KeyboardInterrupt:
        console.print("\n👋 [yellow]Servidor encerrado[/yellow]")

def is_port_free(host, port):
    """Verificar se porta está livre"""
    import socket
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            return True
    except OSError:
        return False

@click.command()
@click.option('--port', '-p', default=3000, help='Porta do servidor de desenvolvimento')
@click.option('--open', '-o', is_flag=True, help='Abrir navegador automaticamente')
def dev_server(port, open):
    """🔧 Servidor de desenvolvimento com hot reload"""
    
    console.print("🔧 [bold blue]PRFI Dev Server[/bold blue]")
    console.print("Iniciando servidor de desenvolvimento...\n")
    
    try:
        # Verificar se Node.js está instalado
        import subprocess
        subprocess.run(["node", "--version"], check=True, capture_output=True)
        
        # Diretório do frontend
        frontend_dir = Path(__file__).parent.parent / "web" / "frontend"
        
        if not frontend_dir.exists():
            console.print("❌ [red]Diretório do frontend não encontrado[/red]")
            console.print("💡 Execute 'prfi init' para configurar o projeto")
            return False
        
        # Instalar dependências se necessário
        node_modules = frontend_dir / "node_modules"
        if not node_modules.exists():
            console.print("📦 [yellow]Instalando dependências...[/yellow]")
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        
        # Configurar variáveis de ambiente
        env = {
            "PORT": str(port),
            "BROWSER": "none" if not open else "default"
        }
        
        # Iniciar servidor de desenvolvimento
        console.print(f"🚀 [green]Servidor iniciado em http://localhost:{port}[/green]")
        
        if open:
            threading.Timer(2.0, lambda: webbrowser.open(f"http://localhost:{port}")).start()
        
        subprocess.run(
            ["npm", "run", "dev"],
            cwd=frontend_dir,
            env={**os.environ, **env}
        )
        
    except subprocess.CalledProcessError:
        console.print("❌ [red]Node.js não está instalado[/red]")
        console.print("💡 Instale Node.js: https://nodejs.org/")
        return False
    except KeyboardInterrupt:
        console.print("\n👋 [yellow]Servidor de desenvolvimento encerrado[/yellow]")
        return True
    except Exception as e:
        console.print(f"❌ [red]Erro no servidor de desenvolvimento: {e}[/red]")
        return False

# Adicionar comando dev ao grupo principal
@click.group()
def dashboard_group():
    """📊 Comandos do dashboard"""
    pass

dashboard_group.add_command(dashboard, name="start")
dashboard_group.add_command(dev_server, name="dev")
