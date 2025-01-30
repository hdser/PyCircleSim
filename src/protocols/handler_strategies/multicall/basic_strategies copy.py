from typing import Dict, Any, Optional
from src.protocols.handler_strategies.base import BaseStrategy
from src.framework.core import SimulationContext
from src.framework.logging import get_logger
import random

logger = get_logger(__name__)

class MultiCallTransactionStrategy(BaseStrategy):
    """Strategy for generating multicall transactions"""
    
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        """Generate parameters for a multicall transaction"""
        sender = self.get_sender(context)
        if not sender:
            return None

        # Initialize with transaction parameters
        all_calls = {
            "tx_params": {
                "sender": sender,
                "value": 0  
            }
        }

        # Get available actions excluding multicall
        available_actions = [
            (name, config) for name, config in context.agent.profile.action_configs.items()
            if (not name.startswith('multiCall_') and 
                context.agent.can_perform_action(name, context.chain.blocks.head.number, {}))
        ]

        if not available_actions:
            return None

        # Select 2-4 random actions
        num_actions = random.randint(2, 4)
        selected_actions = random.sample(
            available_actions, 
            min(num_actions, len(available_actions))
        )

        # Generate parameters for each action
        for action_name, config in selected_actions:
            try:
                # Split into contract and function name
                contract_id = action_name.split('_')[0]
                function_name = action_name[len(contract_id)+1:]

                # Get strategy for this action
                strategy_class = self._get_strategy_class(contract_id, function_name)
                if not strategy_class:
                    continue

                # Generate parameters
                strategy = strategy_class()
                action_params = strategy.get_params(context)
                if not action_params:
                    continue

                # Add to multicall params
                all_calls[action_name] = action_params

            except Exception as e:
                logger.error(f"Error generating params for {action_name}: {e}")
                continue

        # Return None if no valid calls were generated
        return all_calls if len(all_calls) > 1 else None

    def _get_strategy_class(self, contract_id: str, function_name: str):
        """Get strategy class for an action"""
        try:
            # Import strategy module
            module_path = f"src.protocols.handler_strategies.{contract_id}.basic_strategies"
            module = __import__(module_path, fromlist=[f"{function_name}Strategy"])
            return getattr(module, f"{function_name}Strategy")
        except Exception as e:
            logger.error(f"Error getting strategy class: {e}")
            return None