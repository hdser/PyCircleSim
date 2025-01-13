from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from src.framework.core import SimulationContext
import random

class BaseStrategy(ABC):
    """Base class for all parameter generation strategies"""
    
    def __init__(self):
        """Initialize strategy"""
        pass

    @abstractmethod
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        """Get parameters for an action"""
        pass

    def get_sender(self, context: SimulationContext) -> Optional[str]:
        """Helper to get a random account from agent"""
        if not context.agent.accounts:
            return None
        return random.choice(list(context.agent.accounts.keys()))