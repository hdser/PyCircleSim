from typing import Dict, Any
import logging
from ..base import BaseProtocolAction, BaseAgent
from ..registry import ActionConfig
from src.protocols.fjord import PoolConfig, WeightedPoolConfig

logger = logging.getLogger(__name__)

class FjordAction(BaseProtocolAction):
    """Base class for all Fjord protocol actions"""
    PROTOCOL = "fjord"

class CreatePoolAction(FjordAction):
    """Liquidity pool creation action"""
    
    def validate(self, agent: 'BaseAgent', **kwargs) -> bool:
        config = kwargs.get('config')
        return bool(config and isinstance(config, PoolConfig))
        
    def execute(self, agent: 'BaseAgent', **kwargs) -> bool:
        return super().execute(agent, **kwargs)

class ExitPoolAction(FjordAction):
    """Pool exit action"""
    
    def validate(self, agent: 'BaseAgent', **kwargs) -> bool:
        pool = kwargs.get('pool')
        max_out = kwargs.get('max_bpt_token_out')
        return bool(pool and max_out is not None)
        
    def execute(self, agent: 'BaseAgent', **kwargs) -> bool:
        return super().execute(agent, **kwargs)

class CreateWeightedPoolAction(FjordAction):
    """Weighted pool creation action"""
    
    def validate(self, agent: 'BaseAgent', **kwargs) -> bool:
        lbp_pool = kwargs.get('lbp_pool')
        config = kwargs.get('config')
        return bool(lbp_pool and config and isinstance(config, WeightedPoolConfig))
        
    def execute(self, agent: 'BaseAgent', **kwargs) -> bool:
        return super().execute(agent, **kwargs)

class SetSwapEnabledAction(FjordAction):
    """Set swap enabled/disabled action"""
    
    def validate(self, agent: 'BaseAgent', **kwargs) -> bool:
        pool = kwargs.get('pool')
        enabled = kwargs.get('enabled')
        return pool is not None and isinstance(enabled, bool)
        
    def execute(self, agent: 'BaseAgent', **kwargs) -> bool:
        return super().execute(agent, **kwargs)

# Register all actions
CreatePoolAction.register("fjord", "CREATE_POOL")
ExitPoolAction.register("fjord", "EXIT_POOL")
CreateWeightedPoolAction.register("fjord", "CREATE_WEIGHTED_POOL")
SetSwapEnabledAction.register("fjord", "SET_SWAP_ENABLED")