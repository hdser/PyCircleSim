from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("supergroup_trust")
class SuperGroupTrust(BaseImplementation):
    """Implementation for trust in SuperGroup"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate trust call(s).

        Args:
            context: Current simulation context

                _trustReceiver (address): Contract parameter

                _expiry (uint96): Contract parameter


        Returns:
            List[ContractCall]: List of calls to execute
        """
        sender = self.get_sender(context)
        if not sender:
            return []

        client = context.get_client("supergroup")
        if not client:
            return []

        # Get constraints from profile
        constraints = context.agent.profile.get_action_config(
            "supergroup_trust"
        ).constraints

        return [
            ContractCall(
                client_name="supergroup",
                method="trust",
                params={
                    "sender": sender,
                    "value": 0,
                    "_trustReceiver": constraints.get("_trustReceiver"),
                    "_expiry": constraints.get("_expiry"),
                },
            )
        ]
