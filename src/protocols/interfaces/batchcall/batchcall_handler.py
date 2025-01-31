from typing import Dict, Any, Optional, Type
from src.protocols.handler_strategies.base import BaseStrategy
from src.framework.core import SimulationContext
from src.framework.logging import get_logger
from src.protocols.handler_strategies.batchcall.basic_strategies import available_calls
import importlib
import random

logger = get_logger(__name__)

class BatchCallHandler:
    """Handler for batch call operations"""
    
    def __init__(self, client, chain, logger, strategy_name: str = 'basic'):
        """Initialize batch call handler"""
        self.client = client
        self.chain = chain
        self.logger = logger
        
        # Load appropriate strategy
        try:
            module_path = f"src.protocols.handler_strategies.batchcall.{strategy_name}_strategies"
            strategy_module = importlib.import_module(module_path)
            # Look for specific strategies like SetupLBPStrategy in the available_calls
            self.strategy = self  # Default to self if no specific strategy found
            for strategy_class in available_calls.values():
                if isinstance(self, strategy_class):
                    self.strategy = strategy_class()
                    break
        except (ImportError, AttributeError) as e:
            self.logger.error(f"Failed to load strategy {strategy_name}: {e}")
            self.strategy = self

    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        """Retrieve parameters for batch call execution, ensuring sequence consistency."""
        try:
            agent = context.agent
            # Get current sequence state and address
            addresses = list(agent.accounts.keys())
            if not addresses:
                return None

            # Check each address for active sequences
            for address in addresses:
                seq_state = agent.sequence_states.get(address)
                if not seq_state:
                    continue

                # Get active sequence info
                for sequence in agent.profile.sequences:
                    state = seq_state.get(sequence.name, {})
                    if not state.get("active"):
                        continue

                    current_step = state.get("current_step_index", 0)
                    if current_step < len(sequence.steps):
                        step = sequence.steps[current_step]
                        if step.action == "batchcall_BatchCall" and step.batchcall:
                            # Get batchcall type
                            call_type = list(step.batchcall.keys())[0]
                            strategy_class = available_calls.get(call_type)
                            if strategy_class:
                                strategy = strategy_class()
                                batch_params = strategy.get_params(context)
                                if batch_params:
                                    # The strategy's get_params already includes batch_calls
                                    return batch_params

            self.logger.debug("No active batch call sequences found")
            return None

        except Exception as e:
            self.logger.error(f"Failed to get batch parameters: {e}")
            return None

    def execute(self, context: SimulationContext, params: Dict[str, Any] = None) -> bool:
        """Execute batch call operation"""
        try:
            if not params:
                params = self.get_params(context)
                if not params:
                    return False

            # Execute batch calls that were prepared by the strategy
            if 'batch_calls' in params:
                return self.client.execute_batch(params['batch_calls'], context)
            else:
                self.logger.error("No batch_calls found in params")
                return False

        except Exception as e:
            self.logger.error(f"Batch call execution failed: {e}")
            return False