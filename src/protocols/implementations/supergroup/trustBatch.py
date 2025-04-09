from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("supergroup_trustBatch")
class SuperGroupTrustBatch(BaseImplementation):
    """Implementation for trustBatch in SuperGroup"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate trustBatch call(s).

        Args:
            context: Current simulation context

                _backers (address[]): Contract parameter

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
            "supergroup_trustBatch"
        ).constraints

        return [
            ContractCall(
                client_name="supergroup",
                method="trustBatch",
                params={
                    "sender": sender,
                    "value": 0,
                    "_backers": constraints.get("_backers"),
                    "_expiry": constraints.get("_expiry"),
                },
            )
        ]
