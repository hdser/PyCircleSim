from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("circleshub_calculateIssuanceWithCheck")
class CirclesHubCalculateIssuanceWithCheck(BaseImplementation):
    """Implementation for calculateIssuanceWithCheck in CirclesHub"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate calculateIssuanceWithCheck call(s).

        Args:
            context: Current simulation context

                _human (address): Contract parameter


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
            "circleshub_calculateIssuanceWithCheck"
        ).constraints

        return [
            ContractCall(
                client_name="circleshub",
                method="calculateIssuanceWithCheck",
                params={
                    "sender": sender,
                    "value": 0,
                    "_human": constraints.get("_human"),
                },
            )
        ]
