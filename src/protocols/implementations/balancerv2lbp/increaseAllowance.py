from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("balancerv2lbp_increaseAllowance")
class BalancerV2LBPIncreaseAllowance(BaseImplementation):
    """Implementation for increaseAllowance in BalancerV2LBP"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate increaseAllowance call(s).

        Args:
            context: Current simulation context

                spender (address): Contract parameter

                addedValue (uint256): Contract parameter


        Returns:
            List[ContractCall]: List of calls to execute
        """
        sender = self.get_sender(context)
        if not sender:
            return []

        client = context.get_client("balancerv2lbp")
        if not client:
            return []

        # Get constraints from profile
        constraints = context.agent.profile.get_action_config(
            "balancerv2lbp_increaseAllowance"
        ).constraints

        return [
            ContractCall(
                client_name="balancerv2lbp",
                method="increaseAllowance",
                params={
                    "sender": sender,
                    "value": 0,
                    "spender": constraints.get("spender"),
                    "addedValue": constraints.get("addedValue"),
                },
            )
        ]
