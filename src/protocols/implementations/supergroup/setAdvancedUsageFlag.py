from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("supergroup_setAdvancedUsageFlag")
class SuperGroupSetAdvancedUsageFlag(BaseImplementation):
    """Implementation for setAdvancedUsageFlag in SuperGroup"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate setAdvancedUsageFlag call(s).

        Args:
            context: Current simulation context

                _flag (bytes32): Contract parameter


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
            "supergroup_setAdvancedUsageFlag"
        ).constraints

        return [
            ContractCall(
                client_name="supergroup",
                method="setAdvancedUsageFlag",
                params={
                    "sender": sender,
                    "value": 0,
                    "_flag": constraints.get("_flag"),
                },
            )
        ]
