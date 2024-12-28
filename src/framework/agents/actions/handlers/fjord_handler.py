from typing import Dict, Any
import logging
from ..base import ProtocolHandler, BaseAgent
from src.protocols.fjord import FjordClient, PoolConfig, WeightedPoolConfig
from src.framework.logging import get_logger

logger = get_logger(__name__)

class FjordHandler(ProtocolHandler):
    """Handler for Fjord protocol actions"""
    
    def __init__(self, client: FjordClient):
        self.client = client
        self.SUPPORTED_ACTIONS = {
            'CREATE_POOL', 'EXIT_POOL', 'SET_SWAP_ENABLED',
            'UPDATE_RECIPIENTS', 'CREATE_WEIGHTED_POOL'
        }
        
    def can_handle(self, action_name: str) -> bool:
        return action_name in self.SUPPORTED_ACTIONS
        
    def validate_state(self, agent: 'BaseAgent', action_name: str, **kwargs) -> bool:
        if action_name == 'CREATE_POOL':
            config = kwargs.get('config')
            return bool(config and isinstance(config, PoolConfig))
        elif action_name == 'EXIT_POOL':
            pool = kwargs.get('pool')
            return bool(pool and self.client.is_pool(pool))
        return True
        
    def execute(self, agent: 'BaseAgent', action_name: str, **kwargs) -> bool:
        try:
            if not self.can_handle(action_name):
                return False
                
            if action_name == 'CREATE_POOL':
                return bool(self.client.create_lbp(kwargs['config']))
                
            elif action_name == 'EXIT_POOL':
                return self.client.exit_pool(
                    kwargs['pool'],
                    kwargs['max_bpt_token_out'],
                    kwargs.get('is_standard_fee', True)
                )
                
            elif action_name == 'SET_SWAP_ENABLED':
                return self.client.set_swap_enabled(
                    kwargs['pool'],
                    kwargs['enabled']
                )
                
            elif action_name == 'CREATE_WEIGHTED_POOL':
                return bool(self.client.create_weighted_pool(
                    kwargs['lbp_pool'],
                    kwargs['config']
                ))
                
            return False
            
        except Exception as e:
            logger.error(f"Failed to execute Fjord action {action_name}: {e}")
            return False