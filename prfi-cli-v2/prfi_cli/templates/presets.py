#!/usr/bin/env python3
"""
PRFI CLI 2.0 - Configuration Presets
Presets de configuração otimizados para diferentes casos de uso
"""

# Presets de configuração PRFI
PRESET_CONFIGS = {
    "balanced": {
        "name": "Balanceado",
        "description": "Configuração equilibrada para a maioria dos casos",
        "retry": {
            "max_attempts": 5,
            "initial_delay": 1.0,
            "max_delay": 300.0,
            "multiplier": 2.0,
            "jitter": True,
            "backoff_strategy": "exponential"
        },
        "fallback": {
            "enabled": True,
            "auto_discover": True,
            "max_fallback_attempts": 3,
            "fallback_delay": 0.5
        },
        "tokenization": {
            "enabled": True,
            "min_difficulty": 4,
            "batch_size": 10,
            "auto_submit": True
        },
        "security": {
            "enable_signature_validation": True,
            "require_https": True,
            "rate_limit_enabled": True,
            "rate_limit_requests": 1000,
            "rate_limit_window": 3600
        }
    },
    
    "aggressive": {
        "name": "Agressivo",
        "description": "Máxima resiliência com muitas tentativas",
        "retry": {
            "max_attempts": 10,
            "initial_delay": 0.5,
            "max_delay": 600.0,
            "multiplier": 1.5,
            "jitter": True,
            "backoff_strategy": "exponential"
        },
        "fallback": {
            "enabled": True,
            "auto_discover": True,
            "max_fallback_attempts": 5,
            "fallback_delay": 0.2
        },
        "tokenization": {
            "enabled": True,
            "min_difficulty": 3,
            "batch_size": 20,
            "auto_submit": True
        },
        "security": {
            "enable_signature_validation": True,
            "require_https": True,
            "rate_limit_enabled": True,
            "rate_limit_requests": 2000,
            "rate_limit_window": 3600
        }
    },
    
    "conservative": {
        "name": "Conservador",
        "description": "Configuração leve com poucas tentativas",
        "retry": {
            "max_attempts": 3,
            "initial_delay": 2.0,
            "max_delay": 120.0,
            "multiplier": 2.5,
            "jitter": True,
            "backoff_strategy": "exponential"
        },
        "fallback": {
            "enabled": True,
            "auto_discover": False,
            "max_fallback_attempts": 2,
            "fallback_delay": 1.0
        },
        "tokenization": {
            "enabled": True,
            "min_difficulty": 5,
            "batch_size": 5,
            "auto_submit": False
        },
        "security": {
            "enable_signature_validation": True,
            "require_https": True,
            "rate_limit_enabled": True,
            "rate_limit_requests": 500,
            "rate_limit_window": 3600
        }
    },
    
    "high_performance": {
        "name": "Alta Performance",
        "description": "Otimizado para alta velocidade e throughput",
        "retry": {
            "max_attempts": 3,
            "initial_delay": 0.1,
            "max_delay": 30.0,
            "multiplier": 2.0,
            "jitter": False,
            "backoff_strategy": "linear"
        },
        "fallback": {
            "enabled": True,
            "auto_discover": True,
            "max_fallback_attempts": 2,
            "fallback_delay": 0.05
        },
        "tokenization": {
            "enabled": True,
            "min_difficulty": 3,
            "batch_size": 50,
            "auto_submit": True
        },
        "security": {
            "enable_signature_validation": False,
            "require_https": False,
            "rate_limit_enabled": False,
            "rate_limit_requests": 10000,
            "rate_limit_window": 3600
        }
    },
    
    "development": {
        "name": "Desenvolvimento",
        "description": "Configuração para ambiente de desenvolvimento",
        "retry": {
            "max_attempts": 2,
            "initial_delay": 0.5,
            "max_delay": 10.0,
            "multiplier": 2.0,
            "jitter": False,
            "backoff_strategy": "exponential"
        },
        "fallback": {
            "enabled": False,
            "auto_discover": False,
            "max_fallback_attempts": 1,
            "fallback_delay": 0.1
        },
        "tokenization": {
            "enabled": False,
            "min_difficulty": 2,
            "batch_size": 1,
            "auto_submit": False
        },
        "security": {
            "enable_signature_validation": False,
            "require_https": False,
            "rate_limit_enabled": False,
            "rate_limit_requests": 1000,
            "rate_limit_window": 3600
        }
    }
}

# Templates de projeto por categoria
PROJECT_TEMPLATES = {
    "ecommerce": {
        "name": "E-commerce",
        "description": "Template para lojas online e marketplaces",
        "preset": "balanced",
        "apis": [
            {
                "name": "Payment Gateway",
                "url": "https://api.stripe.com/v1/charges",
                "method": "POST",
                "fallback_url": "https://api.paypal.com/v1/payments",
                "enabled": True,
                "timeout": 30,
                "headers": {
                    "Content-Type": "application/json"
                }
            },
            {
                "name": "Inventory API",
                "url": "https://api.inventory.com/v1/products",
                "method": "GET",
                "enabled": True,
                "timeout": 15
            },
            {
                "name": "Shipping API",
                "url": "https://api.shipping.com/v1/rates",
                "method": "POST",
                "enabled": True,
                "timeout": 20
            }
        ],
        "blockchain": {
            "network": "bsc-testnet",
            "auto_deploy": True
        }
    },
    
    "fintech": {
        "name": "Fintech",
        "description": "Template para aplicações financeiras",
        "preset": "aggressive",
        "apis": [
            {
                "name": "Banking API",
                "url": "https://api.bank.com/v1/transactions",
                "method": "POST",
                "enabled": True,
                "timeout": 45,
                "headers": {
                    "Authorization": "Bearer ${API_TOKEN}"
                }
            },
            {
                "name": "Credit Check",
                "url": "https://api.credit.com/v1/check",
                "method": "POST",
                "fallback_url": "https://api.backup-credit.com/v1/check",
                "enabled": True,
                "timeout": 30
            },
            {
                "name": "Fraud Detection",
                "url": "https://api.fraud.com/v1/analyze",
                "method": "POST",
                "enabled": True,
                "timeout": 10
            }
        ],
        "blockchain": {
            "network": "polygon-mainnet",
            "auto_deploy": True
        }
    },
    
    "gaming": {
        "name": "Gaming",
        "description": "Template para jogos e aplicações de entretenimento",
        "preset": "high_performance",
        "apis": [
            {
                "name": "Player Stats",
                "url": "https://api.game.com/v1/players",
                "method": "GET",
                "enabled": True,
                "timeout": 5
            },
            {
                "name": "Leaderboard",
                "url": "https://api.game.com/v1/leaderboard",
                "method": "GET",
                "fallback_url": "https://cache.game.com/v1/leaderboard",
                "enabled": True,
                "timeout": 3
            },
            {
                "name": "Achievement API",
                "url": "https://api.game.com/v1/achievements",
                "method": "POST",
                "enabled": True,
                "timeout": 10
            }
        ],
        "blockchain": {
            "network": "polygon-mumbai",
            "auto_deploy": True
        }
    },
    
    "iot": {
        "name": "IoT",
        "description": "Template para dispositivos IoT e sensores",
        "preset": "conservative",
        "apis": [
            {
                "name": "Sensor Data",
                "url": "https://api.iot.com/v1/sensors/data",
                "method": "POST",
                "enabled": True,
                "timeout": 60
            },
            {
                "name": "Device Control",
                "url": "https://api.iot.com/v1/devices/control",
                "method": "PUT",
                "fallback_url": "https://backup.iot.com/v1/devices/control",
                "enabled": True,
                "timeout": 30
            },
            {
                "name": "Analytics",
                "url": "https://api.analytics.com/v1/events",
                "method": "POST",
                "enabled": True,
                "timeout": 15
            }
        ],
        "blockchain": {
            "network": "bsc-mainnet",
            "auto_deploy": True
        }
    },
    
    "social": {
        "name": "Social Media",
        "description": "Template para redes sociais e plataformas de conteúdo",
        "preset": "balanced",
        "apis": [
            {
                "name": "User API",
                "url": "https://api.social.com/v1/users",
                "method": "GET",
                "enabled": True,
                "timeout": 10
            },
            {
                "name": "Content API",
                "url": "https://api.social.com/v1/posts",
                "method": "POST",
                "fallback_url": "https://cdn.social.com/v1/posts",
                "enabled": True,
                "timeout": 20
            },
            {
                "name": "Notification API",
                "url": "https://api.notifications.com/v1/send",
                "method": "POST",
                "enabled": True,
                "timeout": 5
            }
        ],
        "blockchain": {
            "network": "polygon-mainnet",
            "auto_deploy": True
        }
    }
}

# Configurações de rede blockchain
BLOCKCHAIN_NETWORKS = {
    "bsc-testnet": {
        "name": "BSC Testnet",
        "chain_id": 97,
        "rpc_url": "https://data-seed-prebsc-1-s1.binance.org:8545",
        "explorer": "https://testnet.bscscan.com",
        "currency": "BNB",
        "faucet": "https://testnet.binance.org/faucet-smart"
    },
    "bsc-mainnet": {
        "name": "BSC Mainnet",
        "chain_id": 56,
        "rpc_url": "https://bsc-dataseed1.binance.org",
        "explorer": "https://bscscan.com",
        "currency": "BNB",
        "faucet": None
    },
    "polygon-mumbai": {
        "name": "Polygon Mumbai",
        "chain_id": 80001,
        "rpc_url": "https://rpc-mumbai.maticvigil.com",
        "explorer": "https://mumbai.polygonscan.com",
        "currency": "MATIC",
        "faucet": "https://faucet.polygon.technology"
    },
    "polygon-mainnet": {
        "name": "Polygon Mainnet",
        "chain_id": 137,
        "rpc_url": "https://polygon-rpc.com",
        "explorer": "https://polygonscan.com",
        "currency": "MATIC",
        "faucet": None
    }
}

def get_preset_config(preset_name: str) -> dict:
    """Obter configuração de preset"""
    return PRESET_CONFIGS.get(preset_name, PRESET_CONFIGS["balanced"])

def get_project_template(template_name: str) -> dict:
    """Obter template de projeto"""
    return PROJECT_TEMPLATES.get(template_name, PROJECT_TEMPLATES["ecommerce"])

def get_blockchain_network(network_name: str) -> dict:
    """Obter configuração de rede blockchain"""
    return BLOCKCHAIN_NETWORKS.get(network_name, BLOCKCHAIN_NETWORKS["bsc-testnet"])

def list_presets() -> list:
    """Listar todos os presets disponíveis"""
    return [
        {
            "id": key,
            "name": config["name"],
            "description": config["description"]
        }
        for key, config in PRESET_CONFIGS.items()
    ]

def list_templates() -> list:
    """Listar todos os templates disponíveis"""
    return [
        {
            "id": key,
            "name": template["name"],
            "description": template["description"]
        }
        for key, template in PROJECT_TEMPLATES.items()
    ]

def list_networks() -> list:
    """Listar todas as redes blockchain disponíveis"""
    return [
        {
            "id": key,
            "name": network["name"],
            "chain_id": network["chain_id"],
            "currency": network["currency"]
        }
        for key, network in BLOCKCHAIN_NETWORKS.items()
    ]
