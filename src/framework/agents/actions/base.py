from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Protocol
import logging
from ..types import ActionConfig
from .registry import action_registry, ActionProtocol, HandlerProtocol
from src.framework.logging import get_logger

logger = get_logger(__name__)

class Action(ABC):
    """Base class for all protocol actions"""
    
    def __init__(self, config: ActionConfig):
        self.config = config
        
    @abstractmethod
    def validate(self, agent: Any, **kwargs) -> bool:
        """Validate if action can be performed"""
        pass
        
    @abstractmethod
    def execute(self, agent: Any, **kwargs) -> bool:
        """Execute the action"""
        pass
    
    @classmethod
    def register(cls, protocol: str, action_name: str):
        """Register action with the global registry"""
        action_registry.register_action(protocol, action_name, cls)

class ProtocolHandler(ABC):
    """Base class for protocol-specific handlers"""
    
    @abstractmethod
    def can_handle(self, action_name: str) -> bool:
        """Check if handler can process this action"""
        pass
        
    @abstractmethod
    def execute(self, agent: Any, action_name: str, **kwargs) -> bool:
        """Execute protocol-specific action"""
        pass
        
    @abstractmethod
    def validate_state(self, agent: Any, action_name: str, **kwargs) -> bool:
        """Validate protocol state for action"""
        pass

class BaseProtocolAction(Action):
    """Base class for protocol-specific actions"""
    PROTOCOL: str = None
    
    def execute(self, agent: Any, **kwargs) -> bool:
        if not self.PROTOCOL:
            raise ValueError("Protocol must be specified")
            
        handler = action_registry.get_handler(self.PROTOCOL)
        if not handler:
            logger.error(f"No handler registered for protocol: {self.PROTOCOL}")
            return False
            
        return handler.execute(agent, self.__class__.__name__, **kwargs)