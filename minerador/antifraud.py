"""
Sistema anti-fraude para mineração PRFI
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass


@dataclass
class AntifraudRules:
    """Regras de validação anti-fraude"""
    max_events_per_hour: int = 100
    max_events_per_day: int = 1000
    min_request_duration: float = 0.1
    max_points_per_event: float = 1.0


class AntiFraudSystem:
    """Sistema de detecção e prevenção de fraudes"""
    
    def __init__(self, rules: AntifraudRules = None):
        """
        Inicializa o sistema anti-fraude
        
        Args:
            rules: Regras de validação
        """
        self.rules = rules or AntifraudRules()
        self.event_history: Dict[str, List[datetime]] = {}
        self.miner_stats: Dict[str, Dict[str, Any]] = {}
    
    def validate_event(self, miner_address: str, event_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Valida um evento contra regras anti-fraude
        
        Args:
            miner_address: Endereço do minerador
            event_data: Dados do evento
            
        Returns:
            Tuple com (is_valid, errors)
        """
        errors = []
        
        # Verificar rate limiting
        if not self._check_rate_limit(miner_address):
            errors.append("Rate limit excedido")
        
        # Verificar duração da requisição
        request_duration = event_data.get('request_duration', 0.0)
        if request_duration < self.rules.min_request_duration:
            errors.append(f"Requisição muito rápida: {request_duration}s")
        
        # Verificar pontos por evento
        points = event_data.get('points', 0.0)
        if points > self.rules.max_points_per_event:
            errors.append(f"Pontos por evento muito alto: {points}")
        
        # Verificar padrões suspeitos
        if self._detect_suspicious_patterns(miner_address, event_data):
            errors.append("Padrão suspeito detectado")
        
        return len(errors) == 0, errors
    
    def _check_rate_limit(self, miner_address: str) -> bool:
        """Verifica rate limiting para um minerador"""
        now = datetime.utcnow()
        
        # Inicializar histórico se não existir
        if miner_address not in self.event_history:
            self.event_history[miner_address] = []
        
        events = self.event_history[miner_address]
        
        # Remover eventos antigos (mais de 24h)
        cutoff_24h = now - timedelta(hours=24)
        events = [event_time for event_time in events if event_time > cutoff_24h]
        self.event_history[miner_address] = events
        
        # Verificar limite diário
        if len(events) >= self.rules.max_events_per_day:
            return False
        
        # Verificar limite por hora
        cutoff_1h = now - timedelta(hours=1)
        events_last_hour = [event_time for event_time in events if event_time > cutoff_1h]
        if len(events_last_hour) >= self.rules.max_events_per_hour:
            return False
        
        # Adicionar evento atual
        events.append(now)
        
        return True
    
    def _detect_suspicious_patterns(self, miner_address: str, event_data: Dict[str, Any]) -> bool:
        """Detecta padrões suspeitos de comportamento"""
        # Implementação básica - pode ser expandida
        
        # Verificar se há muitos eventos idênticos
        payload_hash = event_data.get('payload_hash', '')
        if not payload_hash:
            return True  # Suspeito se não há hash do payload
        
        # Verificar timing suspeito (muitos eventos no mesmo segundo)
        now = datetime.utcnow()
        events = self.event_history.get(miner_address, [])
        recent_events = [e for e in events if (now - e).total_seconds() < 1]
        
        if len(recent_events) > 5:  # Mais de 5 eventos por segundo é suspeito
            return True
        
        return False
    
    def get_miner_stats(self, miner_address: str) -> Dict[str, Any]:
        """Obtém estatísticas de um minerador"""
        events = self.event_history.get(miner_address, [])
        now = datetime.utcnow()
        
        # Eventos nas últimas 24h
        events_24h = [e for e in events if (now - e).total_seconds() < 86400]
        
        # Eventos na última hora
        events_1h = [e for e in events if (now - e).total_seconds() < 3600]
        
        return {
            'total_events': len(events),
            'events_24h': len(events_24h),
            'events_1h': len(events_1h),
            'rate_limit_status': 'OK' if len(events_24h) < self.rules.max_events_per_day else 'EXCEEDED',
            'last_event': events[-1].isoformat() if events else None
        }


class AntifraudEngine:
    """Engine principal de anti-fraude"""
    
    def __init__(self, rules: AntifraudRules):
        """
        Inicializa o engine anti-fraude
        
        Args:
            rules: Regras de validação
        """
        self.rules = rules
        self.system = AntiFraudSystem(rules)
    
    def validate_block(self, block) -> Tuple[bool, List[str]]:
        """
        Valida um bloco contra regras anti-fraude
        
        Args:
            block: Bloco para validar
            
        Returns:
            Tuple com (is_valid, errors)
        """
        event_data = {
            'request_duration': getattr(block, 'request_duration', 0.0),
            'points': getattr(block, 'points', 0.0),
            'payload_hash': getattr(block, 'payload_hash', ''),
            'response_size': getattr(block, 'response_size', 0)
        }
        
        return self.system.validate_event(block.miner, event_data)
    
    def get_miner_stats(self, miner_address: str) -> Dict[str, Any]:
        """Obtém estatísticas de um minerador"""
        return self.system.get_miner_stats(miner_address)
