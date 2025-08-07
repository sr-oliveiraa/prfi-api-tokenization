"""
Exceções específicas do PRFI.
"""


class PRFIException(Exception):
    """Exceção base para todas as exceções do PRFI."""
    
    def __init__(self, message: str, event_id: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.event_id = event_id
        self.details = details or {}


class RetryExhaustedException(PRFIException):
    """Exceção lançada quando todas as tentativas de retry foram esgotadas."""
    
    def __init__(self, event_id: str, attempts: int, last_error: str = None):
        message = f"Retry esgotado para evento {event_id} após {attempts} tentativas"
        super().__init__(
            message=message,
            event_id=event_id,
            details={
                "attempts": attempts,
                "last_error": last_error
            }
        )


class InvalidSignatureException(PRFIException):
    """Exceção lançada quando a assinatura HMAC é inválida."""
    
    def __init__(self, event_id: str = None):
        message = "Assinatura HMAC inválida"
        super().__init__(
            message=message,
            event_id=event_id,
            details={"security_violation": True}
        )


class StorageException(PRFIException):
    """Exceção relacionada a operações de storage."""
    
    def __init__(self, message: str, storage_type: str = None, operation: str = None):
        super().__init__(
            message=message,
            details={
                "storage_type": storage_type,
                "operation": operation
            }
        )


class ConfigurationException(PRFIException):
    """Exceção relacionada a configuração inválida."""
    
    def __init__(self, message: str, config_field: str = None):
        super().__init__(
            message=message,
            details={"config_field": config_field}
        )


class NetworkException(PRFIException):
    """Exceção relacionada a problemas de rede."""
    
    def __init__(self, message: str, url: str = None, status_code: int = None):
        super().__init__(
            message=message,
            details={
                "url": url,
                "status_code": status_code
            }
        )


class EventNotFoundException(PRFIException):
    """Exceção lançada quando um evento não é encontrado."""
    
    def __init__(self, event_id: str):
        message = f"Evento {event_id} não encontrado"
        super().__init__(
            message=message,
            event_id=event_id
        )


class DuplicateEventException(PRFIException):
    """Exceção lançada quando um evento duplicado é detectado."""
    
    def __init__(self, event_id: str):
        message = f"Evento {event_id} já existe"
        super().__init__(
            message=message,
            event_id=event_id,
            details={"duplicate": True}
        )
