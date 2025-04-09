from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("circlesinflationaryerc20_transferFrom")
class CirclesInflationaryERC20TransferFrom(BaseImplementation):
    """Implementation for transferFrom in CirclesInflationaryERC20"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate transferFrom call(s).

        Args:
            context: Current simulation context

                _from (address): Contract parameter

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
            "circlesinflationaryerc20_transferFrom"
        ).constraints

        return [
            ContractCall(
                client_name="circlesinflationaryerc20",
                method="transferFrom",
                params={
                    "sender": sender,
                    "value": 0,
                    "_from": constraints.get("_from"),
                    "_to": constraints.get("_to"),
                    "_amount": constraints.get("_amount"),
                },
            )
        ]
