from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("supergroup_registerShortName")
class SuperGroupRegisterShortName(BaseImplementation):
    """Implementation for registerShortName in SuperGroup"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate registerShortName call(s).

        Args:
            context: Current simulation context


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
            "supergroup_registerShortName"
        ).constraints

        return [
            ContractCall(
                client_name="supergroup",
                method="registerShortName",
                params={
                    "sender": sender,
                    "value": 0,
                },
            )
        ]
