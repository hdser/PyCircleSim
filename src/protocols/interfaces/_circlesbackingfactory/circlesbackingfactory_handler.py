import random
import importlib
from typing import Dict, Any, Optional
from eth_pydantic_types import HexBytes
from src.framework.core.context import SimulationContext
from src.protocols.interfaces.circlesbackingfactory.circlesbackingfactory_client import CirclesBackingFactoryClient


class CreateLBPBaseHandler:
    """Base handler class for createLBP action."""
    
    def __init__(
        self,
        client: CirclesBackingFactoryClient,
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
            
            
            ,'personalCRC': None  # type: address
            
            
            
            ,'personalCRCAmount': None  # type: uint256
            
            
            
            ,'backingAsset': None  # type: address
            
            
            
            ,'backingAssetAmount': None  # type: uint256
            
            
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
                
                
                'personalCRC': execution_params.get("personalCRC"),
                
                
                
                'personalCRCAmount': execution_params.get("personalCRCAmount"),
                
                
                
                'backingAsset': execution_params.get("backingAsset"),
                
                
                
                'backingAssetAmount': execution_params.get("backingAssetAmount"),
                
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.createLBP(**function_args)

        except Exception as e:
            self.logger.error(f"createLBP action failed: {e}", exc_info=True)
            return False

class CreateLBPHandler(CreateLBPBaseHandler):
    """Concrete handler implementation"""
    pass


class ExitLBPBaseHandler:
    """Base handler class for exitLBP action."""
    
    def __init__(
        self,
        client: CirclesBackingFactoryClient,
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
            
            
            ,'lbp': None  # type: address
            
            
            
            ,'bptAmount': None  # type: uint256
            
            
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
                
                
                'lbp': execution_params.get("lbp"),
                
                
                
                'bptAmount': execution_params.get("bptAmount"),
                
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.exitLBP(**function_args)

        except Exception as e:
            self.logger.error(f"exitLBP action failed: {e}", exc_info=True)
            return False

class ExitLBPHandler(ExitLBPBaseHandler):
    """Concrete handler implementation"""
    pass


class GetPersonalCirclesBaseHandler:
    """Base handler class for getPersonalCircles action."""
    
    def __init__(
        self,
        client: CirclesBackingFactoryClient,
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
            
            
            ,'avatar': None  # type: address
            
            
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
                
                
                'avatar': execution_params.get("avatar"),
                
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.getPersonalCircles(**function_args)

        except Exception as e:
            self.logger.error(f"getPersonalCircles action failed: {e}", exc_info=True)
            return False

class GetPersonalCirclesHandler(GetPersonalCirclesBaseHandler):
    """Concrete handler implementation"""
    pass


class NotifyReleaseBaseHandler:
    """Base handler class for notifyRelease action."""
    
    def __init__(
        self,
        client: CirclesBackingFactoryClient,
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
            
            
            ,'lbp': None  # type: address
            
            
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
                
                
                'lbp': execution_params.get("lbp"),
                
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.notifyRelease(**function_args)

        except Exception as e:
            self.logger.error(f"notifyRelease action failed: {e}", exc_info=True)
            return False

class NotifyReleaseHandler(NotifyReleaseBaseHandler):
    """Concrete handler implementation"""
    pass


class OnERC1155ReceivedBaseHandler:
    """Base handler class for onERC1155Received action."""
    
    def __init__(
        self,
        client: CirclesBackingFactoryClient,
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
            
            
            ,'operator': None  # type: address
            
            
            
            ,'from_': None  # type: address
            
            
            
            ,'id': None  # type: uint256
            
            
            
            ,'amount_value': None  # type: uint256 (renamed from 'value')
            
            
            
            ,'data': None  # type: bytes
            
            
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
                
                
                'operator': execution_params.get("operator"),
                
                
                
                'from_': execution_params.get("from_"),
                
                
                
                'id': execution_params.get("id"),
                
                
                
                'value_': execution_params.get("amount_value"),  # Contract's value parameter
                
                
                
                'data': execution_params.get("data"),
                
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.onERC1155Received(**function_args)

        except Exception as e:
            self.logger.error(f"onERC1155Received action failed: {e}", exc_info=True)
            return False

class OnERC1155ReceivedHandler(OnERC1155ReceivedBaseHandler):
    """Concrete handler implementation"""
    pass


class SetReleaseTimestampBaseHandler:
    """Base handler class for setReleaseTimestamp action."""
    
    def __init__(
        self,
        client: CirclesBackingFactoryClient,
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
            
            
            ,'timestamp': None  # type: uint32
            
            
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
                
                
                'timestamp': execution_params.get("timestamp"),
                
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.setReleaseTimestamp(**function_args)

        except Exception as e:
            self.logger.error(f"setReleaseTimestamp action failed: {e}", exc_info=True)
            return False

class SetReleaseTimestampHandler(SetReleaseTimestampBaseHandler):
    """Concrete handler implementation"""
    pass


class SetSupportedBackingAssetStatusBaseHandler:
    """Base handler class for setSupportedBackingAssetStatus action."""
    
    def __init__(
        self,
        client: CirclesBackingFactoryClient,
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
            
            
            ,'backingAsset': None  # type: address
            
            
            
            ,'status': None  # type: bool
            
            
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
                
                
                'backingAsset': execution_params.get("backingAsset"),
                
                
                
                'status': execution_params.get("status"),
                
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.setSupportedBackingAssetStatus(**function_args)

        except Exception as e:
            self.logger.error(f"setSupportedBackingAssetStatus action failed: {e}", exc_info=True)
            return False

class SetSupportedBackingAssetStatusHandler(SetSupportedBackingAssetStatusBaseHandler):
    """Concrete handler implementation"""
    pass

