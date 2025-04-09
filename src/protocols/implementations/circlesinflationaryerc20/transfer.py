from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("circlesinflationaryerc20_transfer")
class CirclesInflationaryERC20Transfer(BaseImplementation):
    """Implementation for transfer in CirclesInflationaryERC20"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate transfer call(s).

        Args:
            context: Current simulation context

                _to (address): Contract parameter

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
            "circlesinflationaryerc20_transfer"
        ).constraints

        return [
            ContractCall(
                client_name="circlesinflationaryerc20",
                method="transfer",
                params={
                    "sender": sender,
                    "value": 0,
                    "_to": constraints.get("_to"),
                    "_amount": constraints.get("_amount"),
                },
            )
        ]
