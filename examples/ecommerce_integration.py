"""
Exemplo de integração PRFI Protocol em um sistema de e-commerce.

Este exemplo demonstra como usar o PRFI Protocol em um cenário real
de e-commerce, incluindo processamento de pagamentos, envio de webhooks,
e notificações com retry automático e fallback.
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from prfi_core import PRFIClient, PRFIConfig


class EcommerceIntegration:
    """Classe que simula integração de e-commerce com PRFI Protocol."""
    
    def __init__(self, api_key: str, miner_address: str, private_key: str = None):
        """Inicializar integração de e-commerce."""
        # Configuração otimizada para e-commerce
        config = PRFIConfig(
            max_retries=5,  # E-commerce precisa de alta confiabilidade
            retry_delay=2.0,
            exponential_backoff=True,
            max_retry_delay=60.0,
            enable_fallback=True,
            timeout=30.0,
            enable_metrics=True
        )
        
        self.client = PRFIClient(
            api_key=api_key,
            miner_address=miner_address,
            private_key=private_key,
            config=config
        )
        
        # URLs dos serviços (simuladas)
        self.payment_api = "https://api.pagamento.com"
        self.payment_fallback = "https://backup.pagamento.com"
        self.notification_api = "https://api.notificacao.com"
        self.webhook_endpoints = []
    
    async def processar_pedido(self, pedido: Dict) -> Dict:
        """Processar um pedido completo com todas as integrações."""
        print(f"🛒 Processando pedido {pedido['id']}")
        
        resultado = {
            "pedido_id": pedido["id"],
            "status": "processando",
            "etapas": {},
            "tokens_ganhos": 0.0,
            "tempo_total": 0
        }
        
        start_time = datetime.now()
        
        try:
            # 1. Validar dados do pedido
            print("   1️⃣ Validando dados do pedido...")
            validacao = await self._validar_pedido(pedido)
            resultado["etapas"]["validacao"] = validacao
            resultado["tokens_ganhos"] += validacao.get("tokens", 0)
            
            if not validacao["sucesso"]:
                resultado["status"] = "erro_validacao"
                return resultado
            
            # 2. Processar pagamento
            print("   2️⃣ Processando pagamento...")
            pagamento = await self._processar_pagamento(pedido)
            resultado["etapas"]["pagamento"] = pagamento
            resultado["tokens_ganhos"] += pagamento.get("tokens", 0)
            
            if not pagamento["sucesso"]:
                resultado["status"] = "erro_pagamento"
                return resultado
            
            # 3. Atualizar estoque
            print("   3️⃣ Atualizando estoque...")
            estoque = await self._atualizar_estoque(pedido)
            resultado["etapas"]["estoque"] = estoque
            resultado["tokens_ganhos"] += estoque.get("tokens", 0)
            
            # 4. Enviar confirmação por email
            print("   4️⃣ Enviando confirmação por email...")
            email = await self._enviar_email_confirmacao(pedido)
            resultado["etapas"]["email"] = email
            resultado["tokens_ganhos"] += email.get("tokens", 0)
            
            # 5. Notificar sistemas externos
            print("   5️⃣ Notificando sistemas externos...")
            notificacoes = await self._enviar_notificacoes(pedido)
            resultado["etapas"]["notificacoes"] = notificacoes
            resultado["tokens_ganhos"] += sum(n.get("tokens", 0) for n in notificacoes)
            
            # 6. Enviar webhooks para parceiros
            print("   6️⃣ Enviando webhooks...")
            webhooks = await self._enviar_webhooks(pedido)
            resultado["etapas"]["webhooks"] = webhooks
            resultado["tokens_ganhos"] += sum(w.get("tokens", 0) for w in webhooks)
            
            resultado["status"] = "concluido"
            print(f"   ✅ Pedido {pedido['id']} processado com sucesso!")
            
        except Exception as e:
            print(f"   ❌ Erro no processamento: {e}")
            resultado["status"] = "erro"
            resultado["erro"] = str(e)
        
        finally:
            end_time = datetime.now()
            resultado["tempo_total"] = (end_time - start_time).total_seconds()
            print(f"   ⏱️ Tempo total: {resultado['tempo_total']:.2f}s")
            print(f"   💰 Tokens ganhos: {resultado['tokens_ganhos']}")
        
        return resultado
    
    async def _validar_pedido(self, pedido: Dict) -> Dict:
        """Validar dados do pedido via API externa."""
        try:
            response = await self.client.request(
                url="https://httpbin.org/post",  # Simular API de validação
                method="POST",
                data={
                    "pedido_id": pedido["id"],
                    "cliente_id": pedido["cliente"]["id"],
                    "items": pedido["items"],
                    "valor_total": pedido["valor_total"]
                },
                headers={"X-Service": "validacao"},
                max_retries=3
            )
            
            return {
                "sucesso": response.success,
                "status_code": response.status_code,
                "tokens": response.points_earned,
                "tempo": response.total_duration
            }
            
        except Exception as e:
            return {
                "sucesso": False,
                "erro": str(e),
                "tokens": 0,
                "tempo": 0
            }
    
    async def _processar_pagamento(self, pedido: Dict) -> Dict:
        """Processar pagamento com fallback."""
        try:
            # Dados do pagamento
            dados_pagamento = {
                "pedido_id": pedido["id"],
                "valor": pedido["valor_total"],
                "moeda": "BRL",
                "metodo": pedido["pagamento"]["metodo"],
                "cartao": {
                    "numero": pedido["pagamento"]["cartao"]["numero_mascarado"],
                    "cvv": "***",
                    "validade": pedido["pagamento"]["cartao"]["validade"]
                },
                "cliente": pedido["cliente"],
                "timestamp": datetime.now().isoformat()
            }
            
            response = await self.client.request(
                url=f"{self.payment_api}/processar",
                method="POST",
                data=dados_pagamento,
                headers={
                    "Authorization": "Bearer payment_token_123",
                    "Content-Type": "application/json"
                },
                fallback_url=f"{self.payment_fallback}/processar",
                max_retries=5,  # Pagamento é crítico
                retry_delay=3.0
            )
            
            return {
                "sucesso": response.success,
                "status_code": response.status_code,
                "transacao_id": f"txn_{uuid.uuid4().hex[:8]}",
                "fallback_usado": response.fallback_used,
                "retries": response.retries_used,
                "tokens": response.points_earned,
                "tempo": response.total_duration
            }
            
        except Exception as e:
            return {
                "sucesso": False,
                "erro": str(e),
                "tokens": 0,
                "tempo": 0
            }
    
    async def _atualizar_estoque(self, pedido: Dict) -> Dict:
        """Atualizar estoque dos produtos."""
        try:
            # Preparar dados de atualização de estoque
            atualizacoes = []
            for item in pedido["items"]:
                atualizacoes.append({
                    "produto_id": item["produto_id"],
                    "quantidade_vendida": item["quantidade"],
                    "estoque_anterior": item.get("estoque_atual", 100),
                    "operacao": "venda"
                })
            
            response = await self.client.request(
                url="https://httpbin.org/put",  # Simular API de estoque
                method="PUT",
                data={
                    "pedido_id": pedido["id"],
                    "atualizacoes": atualizacoes,
                    "timestamp": datetime.now().isoformat()
                },
                headers={"X-Service": "estoque"},
                max_retries=3
            )
            
            return {
                "sucesso": response.success,
                "status_code": response.status_code,
                "produtos_atualizados": len(atualizacoes),
                "tokens": response.points_earned,
                "tempo": response.total_duration
            }
            
        except Exception as e:
            return {
                "sucesso": False,
                "erro": str(e),
                "tokens": 0,
                "tempo": 0
            }
    
    async def _enviar_email_confirmacao(self, pedido: Dict) -> Dict:
        """Enviar email de confirmação do pedido."""
        try:
            email_data = {
                "destinatario": pedido["cliente"]["email"],
                "assunto": f"Confirmação do Pedido #{pedido['id']}",
                "template": "confirmacao_pedido",
                "dados": {
                    "nome_cliente": pedido["cliente"]["nome"],
                    "pedido_id": pedido["id"],
                    "valor_total": pedido["valor_total"],
                    "items": pedido["items"],
                    "data_pedido": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
            }
            
            response = await self.client.request(
                url="https://httpbin.org/post",  # Simular serviço de email
                method="POST",
                data=email_data,
                headers={
                    "X-Service": "email",
                    "Authorization": "Bearer email_token_456"
                },
                max_retries=3,
                retry_delay=1.0
            )
            
            return {
                "sucesso": response.success,
                "status_code": response.status_code,
                "email_enviado": pedido["cliente"]["email"],
                "tokens": response.points_earned,
                "tempo": response.total_duration
            }
            
        except Exception as e:
            return {
                "sucesso": False,
                "erro": str(e),
                "tokens": 0,
                "tempo": 0
            }
    
    async def _enviar_notificacoes(self, pedido: Dict) -> List[Dict]:
        """Enviar notificações para sistemas internos."""
        sistemas = [
            {"nome": "CRM", "url": "https://httpbin.org/post"},
            {"nome": "BI", "url": "https://httpbin.org/post"},
            {"nome": "Logistica", "url": "https://httpbin.org/post"}
        ]
        
        resultados = []
        
        for sistema in sistemas:
            try:
                notificacao_data = {
                    "evento": "pedido.criado",
                    "pedido": {
                        "id": pedido["id"],
                        "cliente_id": pedido["cliente"]["id"],
                        "valor_total": pedido["valor_total"],
                        "status": "confirmado",
                        "timestamp": datetime.now().isoformat()
                    },
                    "sistema_origem": "ecommerce",
                    "sistema_destino": sistema["nome"].lower()
                }
                
                response = await self.client.request(
                    url=sistema["url"],
                    method="POST",
                    data=notificacao_data,
                    headers={
                        "X-Sistema": sistema["nome"],
                        "X-Evento": "pedido.criado"
                    },
                    max_retries=2
                )
                
                resultados.append({
                    "sistema": sistema["nome"],
                    "sucesso": response.success,
                    "status_code": response.status_code,
                    "tokens": response.points_earned,
                    "tempo": response.total_duration
                })
                
            except Exception as e:
                resultados.append({
                    "sistema": sistema["nome"],
                    "sucesso": False,
                    "erro": str(e),
                    "tokens": 0,
                    "tempo": 0
                })
        
        return resultados
    
    async def _enviar_webhooks(self, pedido: Dict) -> List[Dict]:
        """Enviar webhooks para parceiros externos."""
        # Simular webhooks de parceiros
        webhooks = [
            {
                "parceiro": "Marketplace A",
                "url": "https://httpbin.org/post",
                "secret": "webhook_secret_123"
            },
            {
                "parceiro": "Sistema de Frete",
                "url": "https://httpbin.org/post", 
                "secret": "webhook_secret_456"
            }
        ]
        
        resultados = []
        
        for webhook in webhooks:
            try:
                webhook_data = {
                    "event": "order.created",
                    "order": {
                        "id": pedido["id"],
                        "customer": pedido["cliente"],
                        "items": pedido["items"],
                        "total": pedido["valor_total"],
                        "status": "confirmed",
                        "created_at": datetime.now().isoformat()
                    },
                    "webhook_id": str(uuid.uuid4()),
                    "timestamp": datetime.now().isoformat()
                }
                
                # Simular assinatura do webhook
                signature = f"sha256=webhook_signature_{webhook['secret']}"
                
                response = await self.client.request(
                    url=webhook["url"],
                    method="POST",
                    data=webhook_data,
                    headers={
                        "Content-Type": "application/json",
                        "X-Webhook-Signature": signature,
                        "X-Webhook-Event": "order.created",
                        "User-Agent": "EcommerceWebhook/1.0"
                    },
                    max_retries=5,  # Webhooks precisam de muitos retries
                    retry_delay=2.0,
                    exponential_backoff=True
                )
                
                resultados.append({
                    "parceiro": webhook["parceiro"],
                    "sucesso": response.success,
                    "status_code": response.status_code,
                    "retries": response.retries_used,
                    "tokens": response.points_earned,
                    "tempo": response.total_duration
                })
                
            except Exception as e:
                resultados.append({
                    "parceiro": webhook["parceiro"],
                    "sucesso": False,
                    "erro": str(e),
                    "tokens": 0,
                    "tempo": 0
                })
        
        return resultados


async def simular_pedidos():
    """Simular processamento de múltiplos pedidos."""
    print("🛒 Simulação de E-commerce com PRFI Protocol")
    print("=" * 60)
    
    # Configurar integração
    integration = EcommerceIntegration(
        api_key="ecommerce_api_key_789",
        miner_address="0x742d35Cc6634C0532925a3b8D4C9db96590c6C87"
    )
    
    # Simular pedidos
    pedidos = [
        {
            "id": "PED001",
            "cliente": {
                "id": "CLI001",
                "nome": "João Silva",
                "email": "joao@email.com",
                "telefone": "(11) 99999-9999"
            },
            "items": [
                {
                    "produto_id": "PROD001",
                    "nome": "Camiseta Azul",
                    "quantidade": 2,
                    "preco_unitario": 29.90,
                    "estoque_atual": 50
                },
                {
                    "produto_id": "PROD002", 
                    "nome": "Calça Jeans",
                    "quantidade": 1,
                    "preco_unitario": 89.90,
                    "estoque_atual": 25
                }
            ],
            "valor_total": 149.70,
            "pagamento": {
                "metodo": "cartao_credito",
                "cartao": {
                    "numero_mascarado": "**** **** **** 1234",
                    "validade": "12/25"
                }
            }
        },
        {
            "id": "PED002",
            "cliente": {
                "id": "CLI002",
                "nome": "Maria Santos",
                "email": "maria@email.com",
                "telefone": "(11) 88888-8888"
            },
            "items": [
                {
                    "produto_id": "PROD003",
                    "nome": "Tênis Esportivo",
                    "quantidade": 1,
                    "preco_unitario": 199.90,
                    "estoque_atual": 15
                }
            ],
            "valor_total": 199.90,
            "pagamento": {
                "metodo": "pix",
                "pix": {
                    "chave": "maria@email.com"
                }
            }
        }
    ]
    
    # Processar pedidos
    resultados = []
    total_tokens = 0.0
    
    for pedido in pedidos:
        print(f"\n{'='*40}")
        resultado = await integration.processar_pedido(pedido)
        resultados.append(resultado)
        total_tokens += resultado["tokens_ganhos"]
        
        # Aguardar um pouco entre pedidos
        await asyncio.sleep(1)
    
    # Resumo final
    print(f"\n{'='*60}")
    print("📊 RESUMO DA SIMULAÇÃO")
    print(f"{'='*60}")
    
    sucessos = sum(1 for r in resultados if r["status"] == "concluido")
    falhas = len(resultados) - sucessos
    tempo_total = sum(r["tempo_total"] for r in resultados)
    
    print(f"📦 Pedidos processados: {len(resultados)}")
    print(f"✅ Sucessos: {sucessos}")
    print(f"❌ Falhas: {falhas}")
    print(f"⏱️ Tempo total: {tempo_total:.2f}s")
    print(f"💰 Total de tokens PRFIC ganhos: {total_tokens:.2f}")
    print(f"💵 Valor estimado: ${total_tokens * 0.10:.2f} USD")  # Assumindo $0.10 por token
    
    # Detalhes por pedido
    print(f"\n📋 DETALHES POR PEDIDO:")
    for resultado in resultados:
        status_emoji = "✅" if resultado["status"] == "concluido" else "❌"
        print(f"{status_emoji} {resultado['pedido_id']}: {resultado['status']} - {resultado['tokens_ganhos']:.2f} tokens")


if __name__ == "__main__":
    # Executar simulação
    asyncio.run(simular_pedidos())
