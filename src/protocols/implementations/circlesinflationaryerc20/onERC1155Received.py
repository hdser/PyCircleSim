from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("circlesinflationaryerc20_onERC1155Received")
class CirclesInflationaryERC20OnERC1155Received(BaseImplementation):
    """Implementation for onERC1155Received in CirclesInflationaryERC20"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate onERC1155Received call(s).

        Args:
            context: Current simulation context

                 (address): Contract parameter

                _from (address): Contract parameter

                _id (uint256): Contract parameter

                _amount (uint256): Contract parameter

                 (bytes): Contract parameter


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
            "circlesinflationaryerc20_onERC1155Received"
        ).constraints

        return [
            ContractCall(
                client_name="circlesinflationaryerc20",
                method="onERC1155Received",
                params={
                    "sender": sender,
                    "value": 0,
                    "": constraints.get(""),
                    "_from": constraints.get("_from"),
                    "_id": constraints.get("_id"),
                    "_amount": constraints.get("_amount"),
                    "": constraints.get(""),
                },
            )
        ]
