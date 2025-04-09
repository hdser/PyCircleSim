from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("supergroup_setMintFee")
class SuperGroupSetMintFee(BaseImplementation):
    """Implementation for setMintFee in SuperGroup"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate setMintFee call(s).

        Args:
            context: Current simulation context

                _mintFee (uint256): Contract parameter

                _feeCollection (address): Contract parameter


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
            "supergroup_setMintFee"
        ).constraints

        return [
            ContractCall(
                client_name="supergroup",
                method="setMintFee",
                params={
                    "sender": sender,
                    "value": 0,
                    "_mintFee": constraints.get("_mintFee"),
                    "_feeCollection": constraints.get("_feeCollection"),
                },
            )
        ]
