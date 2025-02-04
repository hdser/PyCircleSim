from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("circleshub_wrap")
class CirclesHubWrap(BaseImplementation):
    """Implementation for wrap in CirclesHub"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate wrap call(s).

        Args:
            context: Current simulation context

                _avatar (address): Contract parameter

                _amount (uint256): Contract parameter

                _type (uint8): Contract parameter


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
            "circleshub_wrap"
        ).constraints

        return [
            ContractCall(
                client_name="circleshub",
                method="wrap",
                params={
                    "sender": sender,
                    "value": 0,
                    "_avatar": constraints.get("_avatar"),
                    "_amount": constraints.get("_amount"),
                    "_type": constraints.get("_type"),
                },
            )
        ]
