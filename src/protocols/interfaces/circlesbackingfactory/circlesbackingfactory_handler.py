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
        return {
            'sender': next(iter(context.agent.accounts.keys())) if context.agent.accounts else None,
            'value': 0,
            
            'personalCRC': None,  # type: address
            
            'personalCRCAmount': None,  # type: uint256
            
            'backingAsset': None,  # type: address
            
            'backingAssetAmount': None,  # type: uint256
            
        }

    def execute(self, context: SimulationContext, params: Optional[Dict[str, Any]] = None) -> bool:
        try:
            execution_params = params if params else self.strategy.get_params(context)
            if not execution_params:
                return False
                
            return self.client.createLBP(
                
                personalCRC=execution_params.get("personalCRC"),
                
                personalCRCAmount=execution_params.get("personalCRCAmount"),
                
                backingAsset=execution_params.get("backingAsset"),
                
                backingAssetAmount=execution_params.get("backingAssetAmount"),
                
                sender=execution_params.get("sender"),
                value=execution_params.get("value", 0)
            )

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
        return {
            'sender': next(iter(context.agent.accounts.keys())) if context.agent.accounts else None,
            'value': 0,
            
            'lbp': None,  # type: address
            
            'bptAmount': None,  # type: uint256
            
        }

    def execute(self, context: SimulationContext, params: Optional[Dict[str, Any]] = None) -> bool:
        try:
            execution_params = params if params else self.strategy.get_params(context)
            if not execution_params:
                return False
                
            return self.client.exitLBP(
                
                lbp=execution_params.get("lbp"),
                
                bptAmount=execution_params.get("bptAmount"),
                
                sender=execution_params.get("sender"),
                value=execution_params.get("value", 0)
            )

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
        return {
            'sender': next(iter(context.agent.accounts.keys())) if context.agent.accounts else None,
            'value': 0,
            
            'avatar': None,  # type: address
            
        }

    def execute(self, context: SimulationContext, params: Optional[Dict[str, Any]] = None) -> bool:
        try:
            execution_params = params if params else self.strategy.get_params(context)
            if not execution_params:
                return False
                
            return self.client.getPersonalCircles(
                
                avatar=execution_params.get("avatar"),
                
                sender=execution_params.get("sender"),
                value=execution_params.get("value", 0)
            )

        except Exception as e:
            self.logger.error(f"getPersonalCircles action failed: {e}", exc_info=True)
            return False

class GetPersonalCirclesHandler(GetPersonalCirclesBaseHandler):
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
        return {
            'sender': next(iter(context.agent.accounts.keys())) if context.agent.accounts else None,
            'value': 0,
            
            'operator': None,  # type: address
            
            'from_': None,  # type: address
            
            'id': None,  # type: uint256
            
            'value': None,  # type: uint256
            
            'data': None,  # type: bytes
            
        }

    def execute(self, context: SimulationContext, params: Optional[Dict[str, Any]] = None) -> bool:
        try:
            execution_params = params if params else self.strategy.get_params(context)
            if not execution_params:
                return False
                
            return self.client.onERC1155Received(
                
                operator=execution_params.get("operator"),
                
                from_=execution_params.get("from_"),
                
                id=execution_params.get("id"),
                
                value=execution_params.get("value"),
                
                data=execution_params.get("data"),
                
                sender=execution_params.get("sender"),
                value=execution_params.get("value", 0)
            )

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
        return {
            'sender': next(iter(context.agent.accounts.keys())) if context.agent.accounts else None,
            'value': 0,
            
            'timestamp': None,  # type: uint32
            
        }

    def execute(self, context: SimulationContext, params: Optional[Dict[str, Any]] = None) -> bool:
        try:
            execution_params = params if params else self.strategy.get_params(context)
            if not execution_params:
                return False
                
            return self.client.setReleaseTimestamp(
                
                timestamp=execution_params.get("timestamp"),
                
                sender=execution_params.get("sender"),
                value=execution_params.get("value", 0)
            )

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
        return {
            'sender': next(iter(context.agent.accounts.keys())) if context.agent.accounts else None,
            'value': 0,
            
            'backingAsset': None,  # type: address
            
            'status': None,  # type: bool
            
        }

    def execute(self, context: SimulationContext, params: Optional[Dict[str, Any]] = None) -> bool:
        try:
            execution_params = params if params else self.strategy.get_params(context)
            if not execution_params:
                return False
                
            return self.client.setSupportedBackingAssetStatus(
                
                backingAsset=execution_params.get("backingAsset"),
                
                status=execution_params.get("status"),
                
                sender=execution_params.get("sender"),
                value=execution_params.get("value", 0)
            )

        except Exception as e:
            self.logger.error(f"setSupportedBackingAssetStatus action failed: {e}", exc_info=True)
            return False

class SetSupportedBackingAssetStatusHandler(SetSupportedBackingAssetStatusBaseHandler):
    """Concrete handler implementation"""
    pass

