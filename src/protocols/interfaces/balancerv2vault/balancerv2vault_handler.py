import random
import importlib
from typing import Dict, Any, Optional
from eth_pydantic_types import HexBytes
from src.framework.core.context import SimulationContext
from src.protocols.interfaces.balancerv2vault.balancerv2vault_client import BalancerV2VaultClient


class BatchSwapBaseHandler:
    """Base handler class for batchSwap action."""
    
    def __init__(
        self,
        client: BalancerV2VaultClient,
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
            
            
            ,'kind': None  # type: uint8
            
            
            
            ,'swaps': None  # type: tuple[]
            
            
            
            ,'assets': None  # type: address[]
            
            
            
            ,'funds': None  # type: tuple
            
            
            
            ,'limits': None  # type: int256[]
            
            
            
            ,'deadline': None  # type: uint256
            
            
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
                
                
                'kind': execution_params.get("kind"),
                
                
                
                'swaps': execution_params.get("swaps"),
                
                
                
                'assets': execution_params.get("assets"),
                
                
                
                'funds': execution_params.get("funds"),
                
                
                
                'limits': execution_params.get("limits"),
                
                
                
                'deadline': execution_params.get("deadline"),
                
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.batchSwap(**function_args)

        except Exception as e:
            self.logger.error(f"batchSwap action failed: {e}", exc_info=True)
            return False

class BatchSwapHandler(BatchSwapBaseHandler):
    """Concrete handler implementation"""
    pass


class DeregisterTokensBaseHandler:
    """Base handler class for deregisterTokens action."""
    
    def __init__(
        self,
        client: BalancerV2VaultClient,
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
            
            
            ,'poolId': None  # type: bytes32
            
            
            
            ,'tokens': None  # type: address[]
            
            
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
                
                
                'poolId': execution_params.get("poolId"),
                
                
                
                'tokens': execution_params.get("tokens"),
                
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.deregisterTokens(**function_args)

        except Exception as e:
            self.logger.error(f"deregisterTokens action failed: {e}", exc_info=True)
            return False

class DeregisterTokensHandler(DeregisterTokensBaseHandler):
    """Concrete handler implementation"""
    pass


class ExitPoolBaseHandler:
    """Base handler class for exitPool action."""
    
    def __init__(
        self,
        client: BalancerV2VaultClient,
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
            
            
            ,'poolId': None  # type: bytes32
            
            
            
            ,'sender_account': None  # type: address (renamed from 'sender')
            
            
            
            ,'recipient': None  # type: address
            
            
            
            ,'request': None  # type: tuple
            
            
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
                
                
                'poolId': execution_params.get("poolId"),
                
                
                
                'sender_': execution_params.get("sender_account"),  # Contract's sender parameter
                
                
                
                'recipient': execution_params.get("recipient"),
                
                
                
                'request': execution_params.get("request"),
                
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.exitPool(**function_args)

        except Exception as e:
            self.logger.error(f"exitPool action failed: {e}", exc_info=True)
            return False

class ExitPoolHandler(ExitPoolBaseHandler):
    """Concrete handler implementation"""
    pass


class FlashLoanBaseHandler:
    """Base handler class for flashLoan action."""
    
    def __init__(
        self,
        client: BalancerV2VaultClient,
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
            
            
            ,'recipient': None  # type: address
            
            
            
            ,'tokens': None  # type: address[]
            
            
            
            ,'amounts': None  # type: uint256[]
            
            
            
            ,'userData': None  # type: bytes
            
            
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
                
                
                'recipient': execution_params.get("recipient"),
                
                
                
                'tokens': execution_params.get("tokens"),
                
                
                
                'amounts': execution_params.get("amounts"),
                
                
                
                'userData': execution_params.get("userData"),
                
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.flashLoan(**function_args)

        except Exception as e:
            self.logger.error(f"flashLoan action failed: {e}", exc_info=True)
            return False

class FlashLoanHandler(FlashLoanBaseHandler):
    """Concrete handler implementation"""
    pass


class JoinPoolBaseHandler:
    """Base handler class for joinPool action."""
    
    def __init__(
        self,
        client: BalancerV2VaultClient,
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
            
            
            ,'poolId': None  # type: bytes32
            
            
            
            ,'sender_account': None  # type: address (renamed from 'sender')
            
            
            
            ,'recipient': None  # type: address
            
            
            
            ,'request': None  # type: tuple
            
            
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
                
                
                'poolId': execution_params.get("poolId"),
                
                
                
                'sender_account': execution_params.get("sender_account"),  # Contract's sender parameter
                
                
                
                'recipient': execution_params.get("recipient"),
                
                
                
                'request': execution_params.get("request"),
                
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.joinPool(**function_args)

        except Exception as e:
            self.logger.error(f"joinPool action failed: {e}", exc_info=True)
            return False

class JoinPoolHandler(JoinPoolBaseHandler):
    """Concrete handler implementation"""
    pass


class ManagePoolBalanceBaseHandler:
    """Base handler class for managePoolBalance action."""
    
    def __init__(
        self,
        client: BalancerV2VaultClient,
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
            
            
            ,'ops': None  # type: tuple[]
            
            
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
                
                
                'ops': execution_params.get("ops"),
                
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.managePoolBalance(**function_args)

        except Exception as e:
            self.logger.error(f"managePoolBalance action failed: {e}", exc_info=True)
            return False

class ManagePoolBalanceHandler(ManagePoolBalanceBaseHandler):
    """Concrete handler implementation"""
    pass


class ManageUserBalanceBaseHandler:
    """Base handler class for manageUserBalance action."""
    
    def __init__(
        self,
        client: BalancerV2VaultClient,
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
            
            
            ,'ops': None  # type: tuple[]
            
            
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
                
                
                'ops': execution_params.get("ops"),
                
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.manageUserBalance(**function_args)

        except Exception as e:
            self.logger.error(f"manageUserBalance action failed: {e}", exc_info=True)
            return False

class ManageUserBalanceHandler(ManageUserBalanceBaseHandler):
    """Concrete handler implementation"""
    pass


class QueryBatchSwapBaseHandler:
    """Base handler class for queryBatchSwap action."""
    
    def __init__(
        self,
        client: BalancerV2VaultClient,
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
            
            
            ,'kind': None  # type: uint8
            
            
            
            ,'swaps': None  # type: tuple[]
            
            
            
            ,'assets': None  # type: address[]
            
            
            
            ,'funds': None  # type: tuple
            
            
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
                
                
                'kind': execution_params.get("kind"),
                
                
                
                'swaps': execution_params.get("swaps"),
                
                
                
                'assets': execution_params.get("assets"),
                
                
                
                'funds': execution_params.get("funds"),
                
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.queryBatchSwap(**function_args)

        except Exception as e:
            self.logger.error(f"queryBatchSwap action failed: {e}", exc_info=True)
            return False

class QueryBatchSwapHandler(QueryBatchSwapBaseHandler):
    """Concrete handler implementation"""
    pass


class RegisterPoolBaseHandler:
    """Base handler class for registerPool action."""
    
    def __init__(
        self,
        client: BalancerV2VaultClient,
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
            
            
            ,'specialization': None  # type: uint8
            
            
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
                
                
                'specialization': execution_params.get("specialization"),
                
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.registerPool(**function_args)

        except Exception as e:
            self.logger.error(f"registerPool action failed: {e}", exc_info=True)
            return False

class RegisterPoolHandler(RegisterPoolBaseHandler):
    """Concrete handler implementation"""
    pass


class RegisterTokensBaseHandler:
    """Base handler class for registerTokens action."""
    
    def __init__(
        self,
        client: BalancerV2VaultClient,
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
            
            
            ,'poolId': None  # type: bytes32
            
            
            
            ,'tokens': None  # type: address[]
            
            
            
            ,'assetManagers': None  # type: address[]
            
            
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
                
                
                'poolId': execution_params.get("poolId"),
                
                
                
                'tokens': execution_params.get("tokens"),
                
                
                
                'assetManagers': execution_params.get("assetManagers"),
                
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.registerTokens(**function_args)

        except Exception as e:
            self.logger.error(f"registerTokens action failed: {e}", exc_info=True)
            return False

class RegisterTokensHandler(RegisterTokensBaseHandler):
    """Concrete handler implementation"""
    pass


class SetAuthorizerBaseHandler:
    """Base handler class for setAuthorizer action."""
    
    def __init__(
        self,
        client: BalancerV2VaultClient,
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
            
            
            ,'newAuthorizer': None  # type: address
            
            
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
                
                
                'newAuthorizer': execution_params.get("newAuthorizer"),
                
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.setAuthorizer(**function_args)

        except Exception as e:
            self.logger.error(f"setAuthorizer action failed: {e}", exc_info=True)
            return False

class SetAuthorizerHandler(SetAuthorizerBaseHandler):
    """Concrete handler implementation"""
    pass


class SetPausedBaseHandler:
    """Base handler class for setPaused action."""
    
    def __init__(
        self,
        client: BalancerV2VaultClient,
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
            
            
            ,'paused': None  # type: bool
            
            
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
                
                
                'paused': execution_params.get("paused"),
                
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.setPaused(**function_args)

        except Exception as e:
            self.logger.error(f"setPaused action failed: {e}", exc_info=True)
            return False

class SetPausedHandler(SetPausedBaseHandler):
    """Concrete handler implementation"""
    pass


class SetRelayerApprovalBaseHandler:
    """Base handler class for setRelayerApproval action."""
    
    def __init__(
        self,
        client: BalancerV2VaultClient,
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
            
            
            ,'sender_account': None  # type: address (renamed from 'sender')
            
            
            
            ,'relayer': None  # type: address
            
            
            
            ,'approved': None  # type: bool
            
            
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
                
                
                'sender_': execution_params.get("sender_account"),  # Contract's sender parameter
                
                
                
                'relayer': execution_params.get("relayer"),
                
                
                
                'approved': execution_params.get("approved"),
                
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.setRelayerApproval(**function_args)

        except Exception as e:
            self.logger.error(f"setRelayerApproval action failed: {e}", exc_info=True)
            return False

class SetRelayerApprovalHandler(SetRelayerApprovalBaseHandler):
    """Concrete handler implementation"""
    pass


class SwapBaseHandler:
    """Base handler class for swap action."""
    
    def __init__(
        self,
        client: BalancerV2VaultClient,
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
            
            
            ,'singleSwap': None  # type: tuple
            
            
            
            ,'funds': None  # type: tuple
            
            
            
            ,'limit': None  # type: uint256
            
            
            
            ,'deadline': None  # type: uint256
            
            
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
                
                
                'singleSwap': execution_params.get("singleSwap"),
                
                
                
                'funds': execution_params.get("funds"),
                
                
                
                'limit': execution_params.get("limit"),
                
                
                
                'deadline': execution_params.get("deadline"),
                
                
                # Add transaction parameters
                'sender': execution_params.get("sender"),
                'value': execution_params.get("value", 0),
                'context': context
            }
                
            return self.client.swap(**function_args)

        except Exception as e:
            self.logger.error(f"swap action failed: {e}", exc_info=True)
            return False

class SwapHandler(SwapBaseHandler):
    """Concrete handler implementation"""
    pass

