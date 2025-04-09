from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("circlesbackingfactory_setReleaseTimestamp")
class CirclesBackingFactorySetReleaseTimestamp(BaseImplementation):
    """Implementation for setReleaseTimestamp in CirclesBackingFactory"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate setReleaseTimestamp call(s).

        Args:
            context: Current simulation context

                timestamp (uint32): Contract parameter


        Returns:
            List[ContractCall]: List of calls to execute
        """
        sender = self.get_sender(context)
        if not sender:
            return []

        client = context.get_client("circlesbackingfactory")
        if not client:
            return []

        # Get constraints from profile
        constraints = context.agent.profile.get_action_config(
            "circlesbackingfactory_setReleaseTimestamp"
        ).constraints

        return [
            ContractCall(
                client_name="circlesbackingfactory",
                method="setReleaseTimestamp",
                params={
                    "sender": sender,
                    "value": 0,
                    "timestamp": constraints.get("timestamp"),
                },
            )
        ]
