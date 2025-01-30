from typing import Dict, Any, Optional
from src.framework.core import SimulationContext
from src.framework.logging import get_logger
import importlib
from src.protocols.interfaces.multicall.multicall_client import MultiCallClient

logger = get_logger(__name__)

class LBPSetupHandler:
    """Handler for multicall transactions"""
    

    def __init__(  
        self,
        client: MultiCallClient,
        chain,
        logger,
        strategy_name: str = "basic"):
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
        
    def execute(self, context: 'SimulationContext', params: Dict[str, Any]) -> bool:
        """
        Execute a multicall transaction
        
        Args:
            context: Simulation context
            params: Transaction parameters including subcalls
        """
        try:
            # Verify parameters
            if not params:
                self.logger.error("No parameters provided")
                return False

            # Execute multicall with context for state updates
            return self.client.multiCall_execute(params, context)

        except Exception as e:
            self.logger.error(f"MultiCall execution failed: {e}")
            return False