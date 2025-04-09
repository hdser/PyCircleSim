from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("circlesbackingfactory_notifyRelease")
class CirclesBackingFactoryNotifyRelease(BaseImplementation):
    """Implementation for notifyRelease in CirclesBackingFactory"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate notifyRelease call(s).

        Args:
            context: Current simulation context

                lbp (address): Contract parameter


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
            "circlesbackingfactory_notifyRelease"
        ).constraints

        return [
            ContractCall(
                client_name="circlesbackingfactory",
                method="notifyRelease",
                params={
                    "sender": sender,
                    "value": 0,
                    "lbp": constraints.get("lbp"),
                },
            )
        ]
