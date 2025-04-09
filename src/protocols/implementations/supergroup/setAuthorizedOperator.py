from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("supergroup_setAuthorizedOperator")
class SuperGroupSetAuthorizedOperator(BaseImplementation):
    """Implementation for setAuthorizedOperator in SuperGroup"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate setAuthorizedOperator call(s).

        Args:
            context: Current simulation context

                _operator (address): Contract parameter

                _authorized (bool): Contract parameter


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
            "supergroup_setAuthorizedOperator"
        ).constraints

        return [
            ContractCall(
                client_name="supergroup",
                method="setAuthorizedOperator",
                params={
                    "sender": sender,
                    "value": 0,
                    "_operator": constraints.get("_operator"),
                    "_authorized": constraints.get("_authorized"),
                },
            )
        ]
