"""
Otimizador de gas para transações blockchain
"""

from typing import Dict, Any, Optional
import time


class GasOptimizer:
    """Otimizador de gas para transações"""
    
    def __init__(self, config=None):
        """
        Inicializa o otimizador
        
        Args:
            config: Configuração do otimizador
        """
        self.config = config or {}
        self.gas_history = []
        self.optimization_stats = {
            'total_optimizations': 0,
            'gas_saved': 0,
            'average_gas_price': 0
        }
    
    def optimize_gas_price(self, current_gas_price: int, priority: str = "normal") -> int:
        """
        Otimiza o preço do gas baseado na prioridade
        
        Args:
            current_gas_price: Preço atual do gas
            priority: Prioridade da transação (low, normal, high)
            
        Returns:
            Preço otimizado do gas
        """
        multipliers = {
            "low": 0.8,
            "normal": 1.0,
            "high": 1.2
        }
        
        multiplier = multipliers.get(priority, 1.0)
        optimized_price = int(current_gas_price * multiplier)
        
        # Aplicar limites mínimos e máximos
        min_gas_price = self.config.get('min_gas_price', 1000000000)  # 1 gwei
        max_gas_price = self.config.get('max_gas_price', 50000000000)  # 50 gwei
        
        optimized_price = max(min_gas_price, min(optimized_price, max_gas_price))
        
        # Registrar otimização
        self.gas_history.append({
            'timestamp': time.time(),
            'original_price': current_gas_price,
            'optimized_price': optimized_price,
            'priority': priority
        })
        
        self.optimization_stats['total_optimizations'] += 1
        self.optimization_stats['gas_saved'] += max(0, current_gas_price - optimized_price)
        
        return optimized_price
    
    def estimate_optimal_gas_limit(self, base_estimate: int, complexity_factor: float = 1.0) -> int:
        """
        Estima o limite de gas ótimo
        
        Args:
            base_estimate: Estimativa base do gas
            complexity_factor: Fator de complexidade da transação
            
        Returns:
            Limite de gas otimizado
        """
        # Aplicar fator de complexidade
        adjusted_estimate = int(base_estimate * complexity_factor)
        
        # Adicionar margem de segurança (20%)
        safety_margin = 1.2
        optimal_limit = int(adjusted_estimate * safety_margin)
        
        # Aplicar limites
        min_gas_limit = self.config.get('min_gas_limit', 21000)
        max_gas_limit = self.config.get('max_gas_limit', 8000000)
        
        optimal_limit = max(min_gas_limit, min(optimal_limit, max_gas_limit))
        
        return optimal_limit
    
    def get_recommended_timing(self, priority: str = "normal") -> Dict[str, Any]:
        """
        Recomenda o melhor timing para submissão
        
        Args:
            priority: Prioridade da transação
            
        Returns:
            Recomendações de timing
        """
        current_hour = time.localtime().tm_hour
        
        # Horários de menor congestionamento (aproximado)
        low_congestion_hours = [2, 3, 4, 5, 6, 7, 8]
        medium_congestion_hours = [9, 10, 11, 22, 23, 0, 1]
        high_congestion_hours = [12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
        
        if current_hour in low_congestion_hours:
            congestion_level = "low"
            recommended_delay = 0
        elif current_hour in medium_congestion_hours:
            congestion_level = "medium"
            recommended_delay = 30 if priority == "low" else 0
        else:
            congestion_level = "high"
            recommended_delay = 300 if priority == "low" else 60 if priority == "normal" else 0
        
        return {
            'congestion_level': congestion_level,
            'recommended_delay_seconds': recommended_delay,
            'current_hour': current_hour,
            'optimal_hours': low_congestion_hours
        }
    
    def calculate_batch_optimization(self, num_transactions: int) -> Dict[str, Any]:
        """
        Calcula otimizações para batch de transações
        
        Args:
            num_transactions: Número de transações no batch
            
        Returns:
            Otimizações recomendadas
        """
        # Gas savings por batching
        individual_gas = 21000 * num_transactions
        batch_gas = 21000 + (15000 * num_transactions)  # Economia por batching
        
        gas_savings = individual_gas - batch_gas
        savings_percentage = (gas_savings / individual_gas) * 100
        
        # Recomendações de batch size
        optimal_batch_size = min(50, max(5, num_transactions))
        
        return {
            'individual_gas_cost': individual_gas,
            'batch_gas_cost': batch_gas,
            'gas_savings': gas_savings,
            'savings_percentage': savings_percentage,
            'optimal_batch_size': optimal_batch_size,
            'recommended_batching': num_transactions >= 3
        }
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas de otimização"""
        if self.gas_history:
            avg_original = sum(h['original_price'] for h in self.gas_history) / len(self.gas_history)
            avg_optimized = sum(h['optimized_price'] for h in self.gas_history) / len(self.gas_history)
            
            self.optimization_stats['average_gas_price'] = avg_optimized
            self.optimization_stats['average_savings_per_tx'] = avg_original - avg_optimized
        
        return self.optimization_stats.copy()
    
    def reset_stats(self):
        """Reseta as estatísticas de otimização"""
        self.gas_history = []
        self.optimization_stats = {
            'total_optimizations': 0,
            'gas_saved': 0,
            'average_gas_price': 0
        }
