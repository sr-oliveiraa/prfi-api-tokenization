"""
Módulo de retry com backoff exponencial e jitter.
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Callable, Optional, TypeVar, Union

from .excecoes import RetryExhaustedException
from .modelos import PRFIEvent, RetryConfig

T = TypeVar('T')


class RetryManager:
    """Gerenciador de retry com backoff exponencial."""
    
    def __init__(self, config: RetryConfig):
        """
        Inicializa o gerenciador de retry.
        
        Args:
            config: Configuração de retry
        """
        self.config = config
    
    def calculate_delay(self, attempt: int) -> float:
        """
        Calcula o delay para uma tentativa específica.
        
        Args:
            attempt: Número da tentativa (1-based)
            
        Returns:
            Delay em segundos
        """
        # Base delay with exponential backoff
        delay = self.config.initial_delay * (self.config.multiplier ** (attempt - 1))
        
        # Apply maximum delay cap
        delay = min(delay, self.config.max_delay)
        
        # Add jitter to prevent thundering herd
        if self.config.jitter:
            # Jitter between 50% and 100% of calculated delay
            jitter_factor = 0.5 + random.random() * 0.5
            delay = delay * jitter_factor
        
        return delay
    
    def calculate_next_attempt_time(self, event: PRFIEvent) -> Optional[datetime]:
        """
        Calcula o timestamp da próxima tentativa.
        
        Args:
            event: Evento PRFI
            
        Returns:
            Timestamp da próxima tentativa ou None se esgotado
        """
        if event.prfi_attempts >= event.prfi_max_attempts:
            return None
        
        next_attempt = event.prfi_attempts + 1
        delay = self.calculate_delay(next_attempt)
        
        base_time = event.last_attempt_at or datetime.utcnow()
        return base_time + timedelta(seconds=delay)
    
    def should_retry(self, event: PRFIEvent, error: Exception) -> bool:
        """
        Determina se um evento deve ser reenviado.
        
        Args:
            event: Evento PRFI
            error: Erro que ocorreu
            
        Returns:
            True se deve tentar novamente
        """
        # Check if max attempts reached
        if event.prfi_attempts >= event.prfi_max_attempts:
            return False
        
        # Check error type - some errors should not be retried
        error_type = type(error).__name__
        non_retryable_errors = [
            'InvalidSignatureException',
            'ConfigurationException',
            'DuplicateEventException'
        ]
        
        if error_type in non_retryable_errors:
            return False
        
        # For HTTP errors, check status code
        if hasattr(error, 'status_code'):
            status_code = error.status_code
            
            # Don't retry client errors (4xx) except rate limiting (429)
            if 400 <= status_code < 500 and status_code != 429:
                return False
        
        return True
    
    async def execute_with_retry(
        self,
        func: Callable[[], T],
        event: PRFIEvent,
        on_retry: Optional[Callable[[PRFIEvent, Exception, int], None]] = None
    ) -> T:
        """
        Executa uma função com retry automático.
        
        Args:
            func: Função a ser executada
            event: Evento PRFI
            on_retry: Callback chamado a cada retry
            
        Returns:
            Resultado da função
            
        Raises:
            RetryExhaustedException: Se todas as tentativas falharem
        """
        last_error = None
        
        for attempt in range(1, event.prfi_max_attempts + 1):
            try:
                # Update attempt count
                event.prfi_attempts = attempt
                event.last_attempt_at = datetime.utcnow()
                
                # Execute function
                result = await func() if asyncio.iscoroutinefunction(func) else func()
                
                # Success - reset next attempt time
                event.next_attempt_at = None
                return result
                
            except Exception as error:
                last_error = error
                
                # Check if should retry
                if not self.should_retry(event, error):
                    break
                
                # Calculate next attempt time
                if attempt < event.prfi_max_attempts:
                    event.next_attempt_at = self.calculate_next_attempt_time(event)
                    
                    # Call retry callback if provided
                    if on_retry:
                        on_retry(event, error, attempt)
                    
                    # Wait for next attempt
                    delay = self.calculate_delay(attempt + 1)
                    await asyncio.sleep(delay)
        
        # All retries exhausted
        event.next_attempt_at = None
        raise RetryExhaustedException(
            event_id=str(event.prfi_event_id),
            attempts=event.prfi_attempts,
            last_error=str(last_error) if last_error else None
        )


class BackoffCalculator:
    """Calculadora de backoff para uso standalone."""
    
    @staticmethod
    def exponential_backoff(
        attempt: int,
        initial_delay: float = 1.0,
        max_delay: float = 300.0,
        multiplier: float = 2.0,
        jitter: bool = True
    ) -> float:
        """
        Calcula delay usando backoff exponencial.
        
        Args:
            attempt: Número da tentativa (1-based)
            initial_delay: Delay inicial em segundos
            max_delay: Delay máximo em segundos
            multiplier: Multiplicador do backoff
            jitter: Se deve adicionar jitter
            
        Returns:
            Delay em segundos
        """
        # Base delay with exponential backoff
        delay = initial_delay * (multiplier ** (attempt - 1))
        
        # Apply maximum delay cap
        delay = min(delay, max_delay)
        
        # Add jitter to prevent thundering herd
        if jitter:
            jitter_factor = 0.5 + random.random() * 0.5
            delay = delay * jitter_factor
        
        return delay
    
    @staticmethod
    def linear_backoff(
        attempt: int,
        initial_delay: float = 1.0,
        max_delay: float = 300.0,
        increment: float = 1.0,
        jitter: bool = True
    ) -> float:
        """
        Calcula delay usando backoff linear.
        
        Args:
            attempt: Número da tentativa (1-based)
            initial_delay: Delay inicial em segundos
            max_delay: Delay máximo em segundos
            increment: Incremento por tentativa
            jitter: Se deve adicionar jitter
            
        Returns:
            Delay em segundos
        """
        # Linear backoff
        delay = initial_delay + (increment * (attempt - 1))
        
        # Apply maximum delay cap
        delay = min(delay, max_delay)
        
        # Add jitter
        if jitter:
            jitter_factor = 0.5 + random.random() * 0.5
            delay = delay * jitter_factor
        
        return delay


def create_retry_manager(config: Union[RetryConfig, dict]) -> RetryManager:
    """Factory function para criar RetryManager."""
    if isinstance(config, dict):
        config = RetryConfig(**config)
    return RetryManager(config)
