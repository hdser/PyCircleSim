import random
import importlib
from typing import Dict, Any, Optional
from eth_pydantic_types import HexBytes
from src.framework.core.context import SimulationContext
from src.protocols.interfaces.circleserc20lift.circleserc20lift_client import CirclesERC20LiftClient


class EnsureERC20BaseHandler:
    """Base handler class for ensureERC20 action."""
    
    def __init__(
        self,
        client: CirclesERC20LiftClient,
        chain,
        logger,
        strategy_name: str = "basic"
    ):
        self.client = client
        self.chain = chain
        self.logger = logger
        
        try:
            module_path = f"src.protocols.handler_strategies.{client.__class__.__name__.lower().replace('client', '')}.{strategy_name}_strategies"
            strategy_module = importlib.import_module(module_path)
            strategy_class = getattr(strategy_module, f"{self.__class__.__name__.replace('Handler', 'Strategy').replace('Base', '')}")
            self.strategy = strategy_class()
        except (ImportError, AttributeError) as e:
            self.logger.error(f"Failed to load strategy {strategy_name}: {e}")
            self.strategy = self

    def get_params(self, context: SimulationContext) -> Dict[str, Any]:
        """Default parameter generation if no strategy is loaded"""
        tx_sender = next(iter(context.agent.accounts.keys())) if context.agent.accounts else None
        
        # Build parameters dictionary with collision handling
        params = {
            'sender': tx_sender,   # Transaction sender
            'value': 0            # Transaction value
            
            
            ,'_avatar': None  # type: address
            
            
            
            ,'_circlesType': None  # type: uint8
            
            
        }
        return params

    def execute(self, context: SimulationContext, params: Optional[Dict[str, Any]] = None) -> bool:
        """Execute the contract function with proper parameter handling"""
        try:
            execution_params = params if params else self.strategy.get_params(context)
            if not execution_params:
                return False
            
            # Build function arguments with collision handling
            function_args = {
                # Add contract function parameters
                
                
                '_avatar': execution_params.get("_avatar"),
                
                
                
                '_circlesType': execution_params.get("_circlesType"),
                
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.ensureERC20(**function_args)

        except Exception as e:
            self.logger.error(f"ensureERC20 action failed: {e}", exc_info=True)
            return False

class EnsureERC20Handler(EnsureERC20BaseHandler):
    """Concrete handler implementation"""
    pass

