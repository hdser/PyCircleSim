import random
import importlib
from typing import Dict, Any, Optional
from eth_pydantic_types import HexBytes
from src.framework.agents import BaseAgent, AgentManager
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

    def get_params(self, agent, agent_manager) -> Dict[str, Any]:
        """Default parameter generation if no strategy is loaded"""
        return {
            'sender': next(iter(agent.accounts.keys())) if agent.accounts else None,
            'value': 0,
            
            'guy': None,  # type: address
            
            'wad': None,  # type: uint256
            
        }

    def execute(self, agent: BaseAgent, agent_manager: AgentManager, params: Optional[Dict[str, Any]] = None) -> bool:
        try:
            execution_params = params if params else self.strategy.get_params(agent, agent_manager, self.client, self.chain)
            if not execution_params:
                return False
                
            return self.client.approve(
                
                guy=execution_params.get("guy"),
                
                wad=execution_params.get("wad"),
                
                sender=execution_params.get("sender"),
                value=execution_params.get("value", 0)
            )

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

    def get_params(self, agent, agent_manager) -> Dict[str, Any]:
        """Default parameter generation if no strategy is loaded"""
        return {
            'sender': next(iter(agent.accounts.keys())) if agent.accounts else None,
            'value': 0,
            
            'src': None,  # type: address
            
            'dst': None,  # type: address
            
            'wad': None,  # type: uint256
            
        }

    def execute(self, agent: BaseAgent, agent_manager: AgentManager, params: Optional[Dict[str, Any]] = None) -> bool:
        try:
            execution_params = params if params else self.strategy.get_params(agent, agent_manager, self.client, self.chain)
            if not execution_params:
                return False
                
            return self.client.transferFrom(
                
                src=execution_params.get("src"),
                
                dst=execution_params.get("dst"),
                
                wad=execution_params.get("wad"),
                
                sender=execution_params.get("sender"),
                value=execution_params.get("value", 0)
            )

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

    def get_params(self, agent, agent_manager) -> Dict[str, Any]:
        """Default parameter generation if no strategy is loaded"""
        return {
            'sender': next(iter(agent.accounts.keys())) if agent.accounts else None,
            'value': 0,
            
            'wad': None,  # type: uint256
            
        }

    def execute(self, agent: BaseAgent, agent_manager: AgentManager, params: Optional[Dict[str, Any]] = None) -> bool:
        try:
            execution_params = params if params else self.strategy.get_params(agent, agent_manager, self.client, self.chain)
            if not execution_params:
                return False
                
            return self.client.withdraw(
                
                wad=execution_params.get("wad"),
                
                sender=execution_params.get("sender"),
                value=execution_params.get("value", 0)
            )

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

    def get_params(self, agent, agent_manager) -> Dict[str, Any]:
        """Default parameter generation if no strategy is loaded"""
        return {
            'sender': next(iter(agent.accounts.keys())) if agent.accounts else None,
            'value': 0,
            
            'dst': None,  # type: address
            
            'wad': None,  # type: uint256
            
        }

    def execute(self, agent: BaseAgent, agent_manager: AgentManager, params: Optional[Dict[str, Any]] = None) -> bool:
        try:
            execution_params = params if params else self.strategy.get_params(agent, agent_manager, self.client, self.chain)
            if not execution_params:
                return False
                
            return self.client.transfer(
                
                dst=execution_params.get("dst"),
                
                wad=execution_params.get("wad"),
                
                sender=execution_params.get("sender"),
                value=execution_params.get("value", 0)
            )

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

    def get_params(self, agent, agent_manager) -> Dict[str, Any]:
        """Default parameter generation if no strategy is loaded"""
        return {
            'sender': next(iter(agent.accounts.keys())) if agent.accounts else None,
            'value': 0,
            
        }

    def execute(self, agent: BaseAgent, agent_manager: AgentManager, params: Optional[Dict[str, Any]] = None) -> bool:
        try:
            execution_params = params if params else self.strategy.get_params(agent, agent_manager, self.client, self.chain)
            if not execution_params:
                return False
                
            return self.client.deposit(
                
                sender=execution_params.get("sender"),
                value=execution_params.get("value", 0)
            )

        except Exception as e:
            self.logger.error(f"deposit action failed: {e}", exc_info=True)
            return False

class DepositHandler(DepositBaseHandler):
    """Concrete handler implementation"""
    pass

