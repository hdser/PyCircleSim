from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("circleshub_burn")
class CirclesHubBurn(BaseImplementation):
    """Implementation for burn in CirclesHub"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate burn call(s).

        Args:
            context: Current simulation context

                _id (uint256): Contract parameter

                _amount (uint256): Contract parameter

                _data (bytes): Contract parameter


        Returns:
            List[ContractCall]: List of calls to execute
        """
        sender = self.get_sender(context)
        if not sender:
            return []

        client = context.get_client("circleshub")
        if not client:
            return []

        # Get constraints from profile
        constraints = context.agent.profile.get_action_config(
            "circleshub_burn"
        ).constraints

        return [
            ContractCall(
                client_name="circleshub",
                method="burn",
                params={
                    "sender": sender,
                    "value": 0,
                    "_id": constraints.get("_id"),
                    "_amount": constraints.get("_amount"),
                    "_data": constraints.get("_data"),
                },
            )
        ]
