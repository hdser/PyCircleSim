import random
import importlib
from typing import Dict, Any, Optional
from eth_pydantic_types import HexBytes
from src.framework.core.context import SimulationContext
from src.protocols.interfaces.wxdai.wxdai_client import WXDAIClient


class ApproveBaseHandler:
    """Base handler class for approve action."""
    
    def __init__(
        self,
        client: WXDAIClient,
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
            
            
            ,'guy': None  # type: address
            
            
            
            ,'wad': None  # type: uint256
            
            
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
                
                
                'guy': execution_params.get("guy"),
                
                
                
                'wad': execution_params.get("wad"),
                
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.approve(**function_args)

        except Exception as e:
            self.logger.error(f"approve action failed: {e}", exc_info=True)
            return False

class ApproveHandler(ApproveBaseHandler):
    """Concrete handler implementation"""
    pass


class TransferFromBaseHandler:
    """Base handler class for transferFrom action."""
    
    def __init__(
        self,
        client: WXDAIClient,
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
            
            
            ,'src': None  # type: address
            
            
            
            ,'dst': None  # type: address
            
            
            
            ,'wad': None  # type: uint256
            
            
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
                
                
                'src': execution_params.get("src"),
                
                
                
                'dst': execution_params.get("dst"),
                
                
                
                'wad': execution_params.get("wad"),
                
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.transferFrom(**function_args)

        except Exception as e:
            self.logger.error(f"transferFrom action failed: {e}", exc_info=True)
            return False

class TransferFromHandler(TransferFromBaseHandler):
    """Concrete handler implementation"""
    pass


class WithdrawBaseHandler:
    """Base handler class for withdraw action."""
    
    def __init__(
        self,
        client: WXDAIClient,
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
            
            
            ,'wad': None  # type: uint256
            
            
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
                
                
                'wad': execution_params.get("wad"),
                
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.withdraw(**function_args)

        except Exception as e:
            self.logger.error(f"withdraw action failed: {e}", exc_info=True)
            return False

class WithdrawHandler(WithdrawBaseHandler):
    """Concrete handler implementation"""
    pass


class TransferBaseHandler:
    """Base handler class for transfer action."""
    
    def __init__(
        self,
        client: WXDAIClient,
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
            
            
            ,'dst': None  # type: address
            
            
            
            ,'wad': None  # type: uint256
            
            
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
                
                
                'dst': execution_params.get("dst"),
                
                
                
                'wad': execution_params.get("wad"),
                
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.transfer(**function_args)

        except Exception as e:
            self.logger.error(f"transfer action failed: {e}", exc_info=True)
            return False

class TransferHandler(TransferBaseHandler):
    """Concrete handler implementation"""
    pass


class DepositBaseHandler:
    """Base handler class for deposit action."""
    
    def __init__(
        self,
        client: WXDAIClient,
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
                
            return self.client.deposit(**function_args)

        except Exception as e:
            self.logger.error(f"deposit action failed: {e}", exc_info=True)
            return False

class DepositHandler(DepositBaseHandler):
    """Concrete handler implementation"""
    pass

