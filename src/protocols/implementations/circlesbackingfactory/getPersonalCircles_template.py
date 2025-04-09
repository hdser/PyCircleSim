from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("circlesbackingfactory_getPersonalCircles")
class CirclesBackingFactoryGetPersonalCircles(BaseImplementation):
    """Implementation for getPersonalCircles in CirclesBackingFactory"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate getPersonalCircles call(s).

        Args:
            context: Current simulation context

                avatar (address): Contract parameter


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
            "circlesbackingfactory_getPersonalCircles"
        ).constraints

        return [
            ContractCall(
                client_name="circlesbackingfactory",
                method="getPersonalCircles",
                params={
                    "sender": sender,
                    "value": 0,
                    "avatar": constraints.get("avatar"),
                },
            )
        ]
