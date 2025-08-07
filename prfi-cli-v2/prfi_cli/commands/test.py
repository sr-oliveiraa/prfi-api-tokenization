#!/usr/bin/env python3
"""
PRFI CLI 2.0 - Test Command
Testes reais de configuração e APIs integrado com PRFI-Core
"""

import click
import asyncio
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live
import aiohttp

from ..utils.config import load_config, ConfigError
from ..utils.banner import show_success_banner, show_error_banner, show_warning_banner

console = Console()

@click.command()
@click.option('--apis', help='Testar APIs específicas (separadas por vírgula)')
@click.option('--blockchain', is_flag=True, help='Testar conexão blockchain')
@click.option('--watch', is_flag=True, help='Modo contínuo (watch)')
@click.option('--timeout', default=30, help='Timeout para testes (segundos)')
@click.option('--verbose', '-v', is_flag=True, help='Output detalhado')
def test(apis, blockchain, watch, timeout, verbose):
    """🧪 Testar configuração e APIs com PRFI-Core"""

    console.print("🧪 [bold blue]PRFI Protocol - Testes Reais[/bold blue]")
    console.print("Integrando com PRFI-Core para testes completos...\n")

    if watch:
        console.print("👀 [yellow]Modo watch ativado - testes contínuos[/yellow]\n")
        run_watch_mode(apis, blockchain, timeout, verbose)
    else:
        run_single_test(apis, blockchain, timeout, verbose)

def run_single_test(apis: str, blockchain: bool, timeout: int, verbose: bool):
    """Executar teste único"""

    try:
        # Carregar configuração
        config = load_config()

        # Executar testes
        results = asyncio.run(execute_tests(config, apis, blockchain, timeout, verbose))

        # Mostrar resultados
        show_test_results(results)

        # Determinar sucesso geral
        all_passed = all(result.get("success", False) for result in results.values())

        if all_passed:
            show_success_banner(
                "Todos os Testes Passaram!",
                "Seu sistema PRFI está funcionando corretamente"
            )
        else:
            show_warning_banner(
                "Alguns Testes Falharam",
                "Verifique os detalhes acima e corrija os problemas"
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
            "Erro nos Testes",
            str(e)
        )
        sys.exit(1)

def run_watch_mode(apis: str, blockchain: bool, timeout: int, verbose: bool):
    """Executar testes em modo contínuo"""

    console.print("🔄 [bold yellow]Modo Watch Ativado[/bold yellow]")
    console.print("Pressione Ctrl+C para parar\n")

    try:
        config = load_config()

        while True:
            console.print(f"🕐 [dim]{time.strftime('%H:%M:%S')} - Executando testes...[/dim]")

            results = asyncio.run(execute_tests(config, apis, blockchain, timeout, verbose))
            show_test_results(results, compact=True)

            console.print("⏳ [dim]Aguardando 30 segundos...[/dim]\n")
            time.sleep(30)

    except KeyboardInterrupt:
        console.print("\n👋 [yellow]Modo watch interrompido[/yellow]")
    except Exception as e:
        show_error_banner("Erro no modo watch", str(e))

async def execute_tests(config: dict, apis: str, blockchain: bool, timeout: int, verbose: bool) -> Dict[str, Any]:
    """Executar todos os testes"""

    results = {}

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console,
    ) as progress:

        # Teste 1: Configuração
        task1 = progress.add_task("🔍 Testando configuração...", total=100)
        results["config"] = test_configuration(config)
        progress.update(task1, completed=100, description="✅ Configuração testada")

        # Teste 2: APIs
        if config.get("apis") or apis:
            task2 = progress.add_task("🌐 Testando APIs...", total=100)
            results["apis"] = await test_apis(config, apis, timeout, verbose)
            progress.update(task2, completed=100, description="✅ APIs testadas")

        # Teste 3: Blockchain
        if blockchain or config.get("blockchain", {}).get("enabled", True):
            task3 = progress.add_task("⛓️ Testando blockchain...", total=100)
            results["blockchain"] = await test_blockchain(config, timeout)
            progress.update(task3, completed=100, description="✅ Blockchain testado")

        # Teste 4: PRFI Core
        task4 = progress.add_task("🚀 Testando PRFI Core...", total=100)
        results["prfi_core"] = await test_prfi_core(config, timeout)
        progress.update(task4, completed=100, description="✅ PRFI Core testado")

    return results

def test_configuration(config: dict) -> Dict[str, Any]:
    """Testar configuração"""

    result = {
        "success": True,
        "details": [],
        "errors": []
    }

    # Verificar seções obrigatórias
    required_sections = ["project", "prfi"]
    for section in required_sections:
        if section not in config:
            result["success"] = False
            result["errors"].append(f"Seção '{section}' não encontrada")
        else:
            result["details"].append(f"Seção '{section}' OK")

    # Verificar configuração PRFI
    if "prfi" in config:
        prfi_config = config["prfi"]

        if "retry" in prfi_config:
            retry = prfi_config["retry"]
            if retry.get("max_attempts", 0) > 0:
                result["details"].append(f"Retry configurado: {retry['max_attempts']} tentativas")
            else:
                result["errors"].append("max_attempts deve ser maior que 0")
                result["success"] = False

    return result

async def test_apis(config: dict, specific_apis: str, timeout: int, verbose: bool) -> Dict[str, Any]:
    """Testar APIs configuradas"""

    result = {
        "success": True,
        "details": [],
        "errors": [],
        "api_results": {}
    }

    apis_to_test = []

    # Determinar quais APIs testar
    if specific_apis:
        api_names = [name.strip() for name in specific_apis.split(",")]
        for api in config.get("apis", []):
            if api.get("name") in api_names:
                apis_to_test.append(api)
    else:
        apis_to_test = config.get("apis", [])

    if not apis_to_test:
        result["details"].append("Nenhuma API configurada para testar")
        return result

    # Testar cada API
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
        for api in apis_to_test:
            api_result = await test_single_api(session, api, verbose)
            result["api_results"][api.get("name", "unknown")] = api_result

            if api_result["success"]:
                result["details"].append(f"API '{api['name']}' OK ({api_result['response_time']:.2f}s)")
            else:
                result["errors"].append(f"API '{api['name']}' falhou: {api_result['error']}")
                result["success"] = False

    return result

async def test_single_api(session: aiohttp.ClientSession, api: dict, verbose: bool) -> Dict[str, Any]:
    """Testar uma API específica"""

    start_time = time.time()

    try:
        url = api.get("url")
        method = api.get("method", "GET").upper()
        headers = api.get("headers", {})

        if method == "GET":
            async with session.get(url, headers=headers) as response:
                response_time = time.time() - start_time

                return {
                    "success": response.status < 400,
                    "status_code": response.status,
                    "response_time": response_time,
                    "error": None if response.status < 400 else f"HTTP {response.status}"
                }
        else:
            # Para outros métodos, fazer request básico
            async with session.request(method, url, headers=headers) as response:
                response_time = time.time() - start_time

                return {
                    "success": response.status < 400,
                    "status_code": response.status,
                    "response_time": response_time,
                    "error": None if response.status < 400 else f"HTTP {response.status}"
                }

    except Exception as e:
        response_time = time.time() - start_time
        return {
            "success": False,
            "status_code": None,
            "response_time": response_time,
            "error": str(e)
        }

async def test_blockchain(config: dict, timeout: int) -> Dict[str, Any]:
    """Testar conexão blockchain"""

    result = {
        "success": True,
        "details": [],
        "errors": []
    }

    try:
        # Importar Web3 dinamicamente
        from web3 import Web3

        blockchain_config = config.get("blockchain", {})
        network = blockchain_config.get("network", "bsc-testnet")

        # URLs RPC por rede
        rpc_urls = {
            "bsc-testnet": "https://data-seed-prebsc-1-s1.binance.org:8545",
            "bsc-mainnet": "https://bsc-dataseed1.binance.org",
            "polygon-mumbai": "https://rpc-mumbai.maticvigil.com",
            "polygon-mainnet": "https://polygon-rpc.com"
        }

        rpc_url = rpc_urls.get(network)
        if not rpc_url:
            result["success"] = False
            result["errors"].append(f"Rede '{network}' não suportada")
            return result

        # Conectar à blockchain com middleware para POA
        from web3.middleware import geth_poa_middleware

        w3 = Web3(Web3.HTTPProvider(rpc_url))

        # Adicionar middleware para redes POA (como BSC)
        if network.startswith("bsc"):
            w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        if not w3.is_connected():
            result["success"] = False
            result["errors"].append(f"Não foi possível conectar à rede {network}")
            return result

        result["details"].append(f"Conectado à rede {network}")

        # Verificar bloco mais recente
        latest_block = w3.eth.get_block('latest')
        result["details"].append(f"Bloco mais recente: {latest_block.number}")

        # Verificar contrato se deployado
        contract_address = blockchain_config.get("contract_address")
        if contract_address:
            code = w3.eth.get_code(contract_address)
            if code and code != b'':
                result["details"].append(f"Contrato encontrado: {contract_address}")
            else:
                result["errors"].append(f"Contrato não encontrado: {contract_address}")
                result["success"] = False

    except ImportError:
        result["success"] = False
        result["errors"].append("web3 não instalado. Execute: pip install web3")
    except Exception as e:
        result["success"] = False
        result["errors"].append(f"Erro blockchain: {str(e)}")

    return result

async def test_prfi_core(config: dict, timeout: int) -> Dict[str, Any]:
    """Testar funcionalidades do PRFI Core"""

    result = {
        "success": True,
        "details": [],
        "errors": []
    }

    try:
        # Verificar se PRFI Core está disponível
        prfi_core_path = Path(__file__).parent.parent.parent.parent / "prfi-core"

        if not prfi_core_path.exists():
            result["success"] = False
            result["errors"].append("PRFI Core não encontrado")
            return result

        result["details"].append("PRFI Core encontrado")

        # Testar importação dos módulos
        sys.path.insert(0, str(prfi_core_path))

        try:
            from modelos import PRFIEvent, EventStatus
            result["details"].append("Modelos PRFI importados com sucesso")
        except ImportError as e:
            result["errors"].append(f"Erro ao importar modelos: {e}")
            result["success"] = False

        try:
            import cliente_descentralizado
            result["details"].append("Cliente descentralizado importado com sucesso")
        except ImportError as e:
            result["errors"].append(f"Erro ao importar cliente: {e}")
            result["success"] = False

        # Testar configuração de retry
        prfi_config = config.get("prfi", {})
        retry_config = prfi_config.get("retry", {})

        if retry_config:
            max_attempts = retry_config.get("max_attempts", 3)
            initial_delay = retry_config.get("initial_delay", 1.0)

            if max_attempts > 0 and initial_delay > 0:
                result["details"].append(f"Configuração retry válida: {max_attempts} tentativas, {initial_delay}s delay")
            else:
                result["errors"].append("Configuração retry inválida")
                result["success"] = False

    except Exception as e:
        result["success"] = False
        result["errors"].append(f"Erro PRFI Core: {str(e)}")
    finally:
        # Remover path adicionado
        if str(prfi_core_path) in sys.path:
            sys.path.remove(str(prfi_core_path))

    return result

def show_test_results(results: Dict[str, Any], compact: bool = False):
    """Mostrar resultados dos testes"""

    if compact:
        # Versão compacta para modo watch
        status_icons = []
        for test_name, result in results.items():
            icon = "✅" if result.get("success", False) else "❌"
            status_icons.append(f"{icon} {test_name}")

        console.print(" | ".join(status_icons))
        return

    # Versão completa
    table = Table(title="📊 Resultados dos Testes")
    table.add_column("Teste", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Detalhes", style="dim")

    for test_name, result in results.items():
        status = "✅ Passou" if result.get("success", False) else "❌ Falhou"

        details = []
        if result.get("details"):
            details.extend(result["details"])
        if result.get("errors"):
            details.extend([f"❌ {error}" for error in result["errors"]])

        details_text = "\n".join(details) if details else "Nenhum detalhe"

        table.add_row(test_name.title(), status, details_text)

    console.print(table)

    # Mostrar detalhes de APIs se disponível
    if "apis" in results and results["apis"].get("api_results"):
        show_api_test_details(results["apis"]["api_results"])

def show_api_test_details(api_results: Dict[str, Any]):
    """Mostrar detalhes dos testes de API"""

    api_table = Table(title="🌐 Detalhes dos Testes de API")
    api_table.add_column("API", style="cyan")
    api_table.add_column("Status", style="bold")
    api_table.add_column("Tempo", style="yellow")
    api_table.add_column("Código", style="dim")

    for api_name, result in api_results.items():
        status = "✅ OK" if result.get("success", False) else "❌ Falhou"
        response_time = f"{result.get('response_time', 0):.2f}s"
        status_code = str(result.get("status_code", "N/A"))

        api_table.add_row(api_name, status, response_time, status_code)

    console.print(api_table)
