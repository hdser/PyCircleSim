from typing import Dict, Any, Optional, Type
from src.protocols.handler_strategies.base import BaseStrategy
from src.framework.core import SimulationContext
from src.framework.logging import get_logger
from src.protocols.handler_strategies.batchcall.basic_strategies import available_calls
import random

logger = get_logger(__name__)

class BatchCallHandler:
    """Handler for batch call operations"""
    
    def __init__(self, client, chain, logger, strategy_name: str = 'basic'):
        """Initialize batch call handler"""
        self.client = client
        self.chain = chain
        self.logger = logger
        # Create strategy attribute to match interface
        self.strategy = self

    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        """Get parameters for batch call execution"""
        try:
            # Get call type from agent's action config
            action_config = context.agent.profile.action_configs['batchcall_BatchCall']
            if not action_config.batchcall:
                self.logger.error("No batch call type configured")
                return None

            # Handle both string and dict configurations
            if isinstance(action_config.batchcall, str):
                call_type = action_config.batchcall
            else:
                # Select call type based on configured probabilities
                call_type = random.choices(
                    list(action_config.batchcall.keys()),
                    weights=list(action_config.batchcall.values())
                )[0]

            self.logger.debug(f"Selected batch call type: {call_type}")
            
            # Get appropriate strategy for call type
            strategy_class = available_calls.get(call_type)
            if not strategy_class:
                self.logger.error(f"No strategy found for call type: {call_type}")
                return None

            # Initialize strategy and get parameters
            strategy = strategy_class()
            batch_params = strategy.get_params(context)
            if not batch_params:
                self.logger.warning("Failed to get batch parameters")
                return None

            # Log parameters for debugging
            self.logger.debug(f"Batch parameters: {batch_params}")
            return batch_params

        except Exception as e:
            self.logger.error(f"Failed to get batch parameters: {e}")
            return None

    def execute(self, context: SimulationContext, params: Dict[str, Any] = None) -> bool:
        """Execute batch call operation"""
        try:
            self.logger.debug(f"BatchCallHandler executing with params: {params}")
            
            if not params:
                params = self.get_params(context)
                if not params:
                    return False

            # Execute batch call
            return self.client.execute_batch(params,context)

        except Exception as e:
            self.logger.error(f"Batch call execution failed: {e}")
            return False