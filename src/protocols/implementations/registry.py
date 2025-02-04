from typing import Dict, Type
from .base import BaseImplementation, ContractCall

# Global implementation registry
IMPLEMENTATIONS: Dict[str, BaseImplementation] = {}

def register_implementation(name: str):
    """Decorator to register implementation"""
    def decorator(cls):
        IMPLEMENTATIONS[name] = cls()
        return cls
    return decorator

# Export ContractCall from base for convenience
__all__ = ['IMPLEMENTATIONS', 'register_implementation', 'ContractCall']