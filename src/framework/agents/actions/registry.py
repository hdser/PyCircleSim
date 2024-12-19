from typing import Dict, Any, Optional, Protocol
import logging

logger = logging.getLogger(__name__)

class ActionHandler(Protocol):
    """Protocol defining what action handlers must implement"""
    def validate(self, agent: Any, params: Dict) -> bool: ...
    def execute(self, agent: Any, params: Dict) -> bool: ...

class ActionRegistry:
    """Central registry for protocol-specific action handlers"""
    
    def __init__(self):
        self._handlers: Dict[str, Dict[str, ActionHandler]] = {}
        
    def register_handler(self, protocol: str, action: str, handler: ActionHandler):
        """Register a handler for a specific protocol action"""
        if protocol not in self._handlers:
            self._handlers[protocol] = {}
        self._handlers[protocol][action] = handler
        logger.info(f"Registered handler for {protocol}.{action}")
        
    def get_handler(self, protocol: str, action: str) -> Optional[ActionHandler]:
        """Get handler for a specific protocol action"""
        return self._handlers.get(protocol, {}).get(action)

    def validate_action(self, protocol: str, action: str, agent: Any, params: Dict) -> bool:
        """Validate an action using its registered handler"""
        handler = self.get_handler(protocol, action)
        if not handler:
            logger.warning(f"No handler found for {protocol}.{action}")
            return False
            
        return handler.validate(agent, params)
        
    def execute_action(self, protocol: str, action: str, agent: Any, params: Dict) -> bool:
        """Execute an action using its registered handler"""
        handler = self.get_handler(protocol, action)
        if not handler:
            logger.warning(f"No handler found for {protocol}.{action}")
            return False
            
        return handler.execute(agent, params)

# Global registry instance
action_registry = ActionRegistry()