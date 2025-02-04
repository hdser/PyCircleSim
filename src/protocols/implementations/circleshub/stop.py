from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("circleshub_stop")
class CirclesHubStop(BaseImplementation):
    """Implementation for stop in CirclesHub"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate stop call(s).

        Args:
            context: Current simulation context


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
            "circleshub_stop"
        ).constraints

        return [
            ContractCall(
                client_name="circleshub",
                method="stop",
                params={
                    "sender": sender,
                    "value": 0,
                },
            )
        ]
