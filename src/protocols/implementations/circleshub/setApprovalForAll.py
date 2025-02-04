from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("circleshub_setApprovalForAll")
class CirclesHubSetApprovalForAll(BaseImplementation):
    """Implementation for setApprovalForAll in CirclesHub"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate setApprovalForAll call(s).

        Args:
            context: Current simulation context

                _operator (address): Contract parameter

                _approved (bool): Contract parameter


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
            "circleshub_setApprovalForAll"
        ).constraints

        return [
            ContractCall(
                client_name="circleshub",
                method="setApprovalForAll",
                params={
                    "sender": sender,
                    "value": 0,
                    "_operator": constraints.get("_operator"),
                    "_approved": constraints.get("_approved"),
                },
            )
        ]
