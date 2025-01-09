from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import random

class BaseStrategy(ABC):
    """Base class for all parameter generation strategies"""
    
    def __init__(self):
        """Initialize strategy"""
        pass

    @abstractmethod
    def get_params(self, agent, client, chain) -> Optional[Dict[str, Any]]:
        """Get parameters for an action"""
        pass

    def get_sender(self, agent) -> Optional[str]:
        """Helper to get a random account from agent"""
        if not agent.accounts:
            return None
        return random.choice(list(agent.accounts.keys()))