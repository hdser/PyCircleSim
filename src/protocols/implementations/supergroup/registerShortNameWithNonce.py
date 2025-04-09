from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("supergroup_registerShortNameWithNonce")
class SuperGroupRegisterShortNameWithNonce(BaseImplementation):
    """Implementation for registerShortNameWithNonce in SuperGroup"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate registerShortNameWithNonce call(s).

        Args:
            context: Current simulation context

                _nonce (uint256): Contract parameter


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
            "supergroup_registerShortNameWithNonce"
        ).constraints

        return [
            ContractCall(
                client_name="supergroup",
                method="registerShortNameWithNonce",
                params={
                    "sender": sender,
                    "value": 0,
                    "_nonce": constraints.get("_nonce"),
                },
            )
        ]
