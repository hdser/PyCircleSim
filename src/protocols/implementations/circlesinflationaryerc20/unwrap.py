from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("circlesinflationaryerc20_unwrap")
class CirclesInflationaryERC20Unwrap(BaseImplementation):
    """Implementation for unwrap in CirclesInflationaryERC20"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate unwrap call(s).

        Args:
            context: Current simulation context

                _amount (uint256): Contract parameter


        Returns:
            List[ContractCall]: List of calls to execute
        """
        sender = self.get_sender(context)
        if not sender:
            return []

        client = context.get_client("circlesinflationaryerc20")
        if not client:
            return []

        # Get constraints from profile
        constraints = context.agent.profile.get_action_config(
            "circlesinflationaryerc20_unwrap"
        ).constraints

        return [
            ContractCall(
                client_name="circlesinflationaryerc20",
                method="unwrap",
                params={
                    "sender": sender,
                    "value": 0,
                    "_amount": constraints.get("_amount"),
                },
            )
        ]
