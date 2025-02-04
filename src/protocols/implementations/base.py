from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
from src.framework.core.context import SimulationContext

@dataclass
class ContractCall:
    """Represents a single contract call"""
    client_name: str
    method: str
    params: Dict[str, Any]

class BaseImplementation(ABC):
    """Base class for all implementations"""
    
    def get_sender(self, context: SimulationContext) -> Optional[str]:
        """Helper to get sender address"""
        if not context.agent.accounts:
            return None
        return next(iter(context.agent.accounts.keys()))

    @abstractmethod
    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """
        Generate contract calls for this implementation.
        
        Args:
            context: Current simulation context containing agent profile, clients, etc.
            
        Returns:
            List of contract calls to execute
        """
        pass