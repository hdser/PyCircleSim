import random
import importlib
from typing import Dict, Any, Optional
from eth_pydantic_types import HexBytes
from src.framework.core.context import SimulationContext
from src.protocols.interfaces.balancerv2lbpfactory.balancerv2lbpfactory_client import BalancerV2LBPFactoryClient


class CreateBaseHandler:
    """Base handler class for create action."""
    
    def __init__(
        self,
        client: BalancerV2LBPFactoryClient,
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
            
            
            ,'name': None  # type: string
            
            
            
            ,'symbol': None  # type: string
            
            
            
            ,'tokens': None  # type: address[]
            
            
            
            ,'weights': None  # type: uint256[]
            
            
            
            ,'swapFeePercentage': None  # type: uint256
            
            
            
            ,'owner': None  # type: address
            
            
            
            ,'swapEnabledOnStart': None  # type: bool
            
            
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
                
                
                'name': execution_params.get("name"),
                
                
                
                'symbol': execution_params.get("symbol"),
                
                
                
                'tokens': execution_params.get("tokens"),
                
                
                
                'weights': execution_params.get("weights"),
                
                
                
                'swapFeePercentage': execution_params.get("swapFeePercentage"),
                
                
                
                'owner': execution_params.get("owner"),
                
                
                
                'swapEnabledOnStart': execution_params.get("swapEnabledOnStart"),
                
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.create(**function_args)

        except Exception as e:
            self.logger.error(f"create action failed: {e}", exc_info=True)
            return False

class CreateHandler(CreateBaseHandler):
    """Concrete handler implementation"""
    pass


class DisableBaseHandler:
    """Base handler class for disable action."""
    
    def __init__(
        self,
        client: BalancerV2LBPFactoryClient,
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
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.disable(**function_args)

        except Exception as e:
            self.logger.error(f"disable action failed: {e}", exc_info=True)
            return False

class DisableHandler(DisableBaseHandler):
    """Concrete handler implementation"""
    pass

