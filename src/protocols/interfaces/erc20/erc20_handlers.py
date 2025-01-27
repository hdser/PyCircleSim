from typing import Dict, Any, Optional
import importlib
from src.framework.core.context import SimulationContext
from .erc20_client import ERC20Client

class ApproveBaseHandler:
    """Base handler class for approve action."""
    
    def __init__(
        self,
        client: ERC20Client,
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
        
        params = {
            'sender': tx_sender,
            'value': 0,
            'token_address': None,
            'spender': None,
            'amount': None
        }
        return params

    def execute(self, context: SimulationContext, params: Optional[Dict[str, Any]] = None) -> bool:
        """Execute the contract function with proper parameter handling"""
        try:
            execution_params = params if params else self.strategy.get_params(context)
            if not execution_params:
                return False
                
            function_args = {
                'token_address': execution_params.get('token_address'),
                'spender': execution_params.get('spender'),
                'amount': execution_params.get('amount'),
                'sender': execution_params.get('sender'),
                'value': execution_params.get('value', 0)
            }
            
            return self.client.approve(**function_args)

        except Exception as e:
            self.logger.error(f"Approve action failed: {e}", exc_info=True)
            return False

class ApproveHandler(ApproveBaseHandler):
    """Concrete handler implementation"""
    pass

class TransferBaseHandler:
    """Base handler class for transfer action."""
    
    def __init__(
        self,
        client: ERC20Client,
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
        tx_sender = next(iter(context.agent.accounts.keys())) if context.agent.accounts else None
        params = {
            'sender': tx_sender,
            'value': 0,
            'token_address': None,
            'to': None,
            'amount': None
        }
        return params

    def execute(self, context: SimulationContext, params: Optional[Dict[str, Any]] = None) -> bool:
        try:
            execution_params = params if params else self.strategy.get_params(context)
            if not execution_params:
                return False
                
            function_args = {
                'token_address': execution_params.get('token_address'),
                'to': execution_params.get('to'),
                'amount': execution_params.get('amount'),
                'sender': execution_params.get('sender'),
                'value': execution_params.get('value', 0)
            }
            
            return self.client.transfer(**function_args)

        except Exception as e:
            self.logger.error(f"Transfer action failed: {e}", exc_info=True)
            return False

class TransferHandler(TransferBaseHandler):
    """Concrete handler implementation"""
    pass

class TransferFromBaseHandler:
    """Base handler class for transferFrom action."""
    
    def __init__(
        self,
        client: ERC20Client,
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
        tx_sender = next(iter(context.agent.accounts.keys())) if context.agent.accounts else None
        params = {
            'sender': tx_sender,
            'value': 0,
            'token_address': None,
            'from': None,
            'to': None,
            'amount': None
        }
        return params

    def execute(self, context: SimulationContext, params: Optional[Dict[str, Any]] = None) -> bool:
        try:
            execution_params = params if params else self.strategy.get_params(context)
            if not execution_params:
                return False
                
            function_args = {
                'token_address': execution_params.get('token_address'),
                'sender': execution_params.get('from'),
                'recipient': execution_params.get('to'),
                'amount': execution_params.get('amount'),
                'tx_sender': execution_params.get('sender'),
                'value': execution_params.get('value', 0)
            }
            
            return self.client.transfer_from(**function_args)

        except Exception as e:
            self.logger.error(f"TransferFrom action failed: {e}", exc_info=True)
            return False

class TransferFromHandler(TransferFromBaseHandler):
    """Concrete handler implementation"""
    pass

class BurnBaseHandler:
    """Base handler class for burn action."""
    
    def __init__(
        self,
        client: ERC20Client,
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
        tx_sender = next(iter(context.agent.accounts.keys())) if context.agent.accounts else None
        params = {
            'sender': tx_sender,
            'value': 0,
            'token_address': None,
            'value': None
        }
        return params

    def execute(self, context: SimulationContext, params: Optional[Dict[str, Any]] = None) -> bool:
        try:
            execution_params = params if params else self.strategy.get_params(context)
            if not execution_params:
                return False
                
            function_args = {
                'token_address': execution_params.get('token_address'),
                'value': execution_params.get('value'),
                'sender': execution_params.get('sender')
            }
            
            return self.client.burn(**function_args)

        except Exception as e:
            self.logger.error(f"Burn action failed: {e}", exc_info=True)
            return False

class BurnHandler(BurnBaseHandler):
    """Concrete handler implementation"""
    pass

class MintBaseHandler:
    """Base handler class for mint action."""
    
    def __init__(
        self,
        client: ERC20Client,
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
        tx_sender = next(iter(context.agent.accounts.keys())) if context.agent.accounts else None
        params = {
            'sender': tx_sender,
            'value': 0,
            'token_address': None,
            'to': None,
            'amount': None
        }
        return params

    def execute(self, context: SimulationContext, params: Optional[Dict[str, Any]] = None) -> bool:
        try:
            execution_params = params if params else self.strategy.get_params(context)
            if not execution_params:
                return False
                
            function_args = {
                'token_address': execution_params.get('token_address'),
                'to': execution_params.get('to'),
                'amount': execution_params.get('amount'),
                'sender': execution_params.get('sender')
            }
            
            return self.client.mint(**function_args)

        except Exception as e:
            self.logger.error(f"Mint action failed: {e}", exc_info=True)
            return False

class MintHandler(MintBaseHandler):
    """Concrete handler implementation"""
    pass