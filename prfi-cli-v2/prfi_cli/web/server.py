#!/usr/bin/env python3
"""
PRFI CLI 2.0 - Web Server
Servidor web para dashboard
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from typing import Dict, Any, List
import asyncio
import time
import random
import sys
import os

# Adicionar prfi-core ao path
prfi_core_path = Path(__file__).parent.parent.parent / "prfi-core"
if prfi_core_path.exists():
    sys.path.insert(0, str(prfi_core_path))

def create_app(config: Dict[str, Any], dev_mode: bool = False) -> FastAPI:
    """Criar aplicação FastAPI"""
    
    app = FastAPI(
        title="PRFI Dashboard API",
        description="API backend para PRFI Protocol Dashboard",
        version="2.0.0"
    )

    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if dev_mode else ["http://localhost:3000", "http://localhost:8080"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Servir arquivos estáticos
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    # Rota principal
    @app.get("/", response_class=HTMLResponse)
    async def dashboard():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>PRFI Dashboard</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    margin: 0; padding: 2rem; background: #f8fafc; color: #1e293b;
                }
                .container { max-width: 1200px; margin: 0 auto; }
                .header { text-align: center; margin-bottom: 3rem; }
                .logo { font-size: 3rem; margin-bottom: 1rem; }
                .title { font-size: 2.5rem; font-weight: bold; color: #3b82f6; margin-bottom: 0.5rem; }
                .subtitle { font-size: 1.2rem; color: #64748b; }
                .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-top: 3rem; }
                .card { background: white; padding: 2rem; border-radius: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
                .card-title { font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }
                .card-content { color: #64748b; line-height: 1.6; }
                .status { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.875rem; font-weight: 500; }
                .status.online { background: #dcfce7; color: #166534; }
                .footer { text-align: center; margin-top: 3rem; color: #64748b; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🚀</div>
                    <h1 class="title">PRFI Dashboard</h1>
                    <p class="subtitle">Interface web moderna para PRFI Protocol</p>
                    <span class="status online">Sistema Online</span>
                </div>
                
                <div class="cards">
                    <div class="card">
                        <h3 class="card-title">📊 Status</h3>
                        <div class="card-content">
                            <p>Dashboard web funcionando perfeitamente!</p>
                            <p>Versão: 2.0.0</p>
                            <p>Modo: Desenvolvimento</p>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3 class="card-title">🎯 Próximos Passos</h3>
                        <div class="card-content">
                            <p>• Complete o setup com <code>prfi init</code></p>
                            <p>• Teste suas APIs com <code>prfi test</code></p>
                            <p>• Faça deploy com <code>prfi deploy</code></p>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3 class="card-title">🔧 Funcionalidades</h3>
                        <div class="card-content">
                            <p>• Retry automático inteligente</p>
                            <p>• Fallback para endpoints alternativos</p>
                            <p>• Tokenização blockchain</p>
                            <p>• Monitoramento em tempo real</p>
                        </div>
                    </div>
                </div>
                
                <div class="footer">
                    <p>PRFI Protocol - Transformando APIs em sistemas resilientes</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    # API endpoints
    @app.get("/api/status")
    async def api_status():
        return {
            "status": "online",
            "version": "2.0.0",
            "timestamp": time.time(),
            "config": {
                "project_name": config.get("project", {}).get("name", "PRFI Project"),
                "network": config.get("blockchain", {}).get("network", "bsc-testnet"),
                "apis_count": len(config.get("apis", [])),
                "monitoring_enabled": config.get("monitoring", {}).get("enabled", True)
            }
        }

    @app.get("/api/dashboard/stats")
    async def dashboard_stats():
        """Obter estatísticas do dashboard"""
        try:
            # Simular dados reais (integrar com PRFI Core depois)
            stats = {
                "totalRequests": random.randint(1000, 5000),
                "successRate": round(random.uniform(95.0, 99.9), 1),
                "avgResponseTime": random.randint(150, 400),
                "tokensEarned": random.randint(100, 1000),
                "activeAPIs": len(config.get("apis", [])),
                "failedRequests": random.randint(10, 100)
            }
            return stats
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/dashboard/activity")
    async def recent_activity():
        """Obter atividade recente"""
        try:
            activities = []
            activity_types = [
                ("API Request", "success", "Stripe Payment API"),
                ("Token Mined", "info", "Batch #1234 processed"),
                ("Fallback Used", "warning", "Primary API failed"),
                ("Deploy Success", "success", "Contract deployed"),
                ("Error Detected", "error", "High response time")
            ]

            for i in range(10):
                activity_type, status, message = random.choice(activity_types)
                activities.append({
                    "id": i + 1,
                    "type": activity_type,
                    "status": status,
                    "message": message,
                    "timestamp": time.time() - (i * 300)  # 5 min intervals
                })

            return activities
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/apis/status")
    async def apis_status():
        """Obter status das APIs configuradas"""
        try:
            apis = config.get("apis", [])
            api_status = []

            for api in apis:
                # Simular status (integrar com testes reais depois)
                status = {
                    "name": api.get("name", "Unknown API"),
                    "url": api.get("url", ""),
                    "status": random.choice(["online", "offline", "warning"]),
                    "response_time": random.randint(100, 500),
                    "success_rate": round(random.uniform(90.0, 99.9), 1),
                    "last_check": time.time()
                }
                api_status.append(status)

            return api_status
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/blockchain/info")
    async def blockchain_info():
        """Obter informações da blockchain"""
        try:
            blockchain_config = config.get("blockchain", {})

            info = {
                "network": blockchain_config.get("network", "bsc-testnet"),
                "contract_address": blockchain_config.get("contract_address"),
                "connected": True,  # Simular conexão
                "latest_block": random.randint(30000000, 35000000),
                "gas_price": f"{random.randint(5, 20)} gwei",
                "tokens_balance": random.randint(1000, 10000)
            }

            return info
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/performance/chart")
    async def performance_chart():
        """Obter dados para gráfico de performance"""
        try:
            # Gerar dados das últimas 24 horas
            data = []
            now = time.time()

            for i in range(24):
                timestamp = now - (i * 3600)  # 1 hora atrás
                hour = time.strftime("%H:00", time.localtime(timestamp))

                data.append({
                    "timestamp": hour,
                    "requests": random.randint(50, 500),
                    "success_rate": round(random.uniform(95.0, 99.9), 1),
                    "response_time": random.randint(150, 400)
                })

            return list(reversed(data))  # Ordem cronológica
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/test/api")
    async def test_api(api_data: dict):
        """Testar uma API específica"""
        try:
            # Integrar com sistema de testes real
            url = api_data.get("url")
            method = api_data.get("method", "GET")

            # Simular teste por enquanto
            await asyncio.sleep(1)  # Simular delay

            result = {
                "success": random.choice([True, True, True, False]),  # 75% sucesso
                "status_code": random.choice([200, 200, 200, 500]),
                "response_time": random.randint(100, 1000),
                "error": None if random.random() > 0.25 else "Connection timeout"
            }

            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/deploy/contract")
    async def deploy_contract(deploy_data: dict):
        """Deploy do smart contract"""
        try:
            network = deploy_data.get("network", "bsc-testnet")

            # Simular deploy (integrar com deploy real depois)
            await asyncio.sleep(3)  # Simular tempo de deploy

            result = {
                "success": True,
                "contract_address": f"0x{''.join(random.choices('0123456789abcdef', k=40))}",
                "transaction_hash": f"0x{''.join(random.choices('0123456789abcdef', k=64))}",
                "network": network,
                "gas_used": random.randint(2000000, 3000000)
            }

            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app
