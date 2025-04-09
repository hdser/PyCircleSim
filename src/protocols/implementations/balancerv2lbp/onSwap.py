from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("balancerv2lbp_onSwap")
class BalancerV2LBPOnSwap(BaseImplementation):
    """Implementation for onSwap in BalancerV2LBP"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate onSwap call(s).

        Args:
            context: Current simulation context

                request (tuple): Contract parameter

                balanceTokenIn (uint256): Contract parameter

                balanceTokenOut (uint256): Contract parameter


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
            "balancerv2lbp_onSwap"
        ).constraints

        return [
            ContractCall(
                client_name="balancerv2lbp",
                method="onSwap",
                params={
                    "sender": sender,
                    "value": 0,
                    "request": constraints.get("request"),
                    "balanceTokenIn": constraints.get("balanceTokenIn"),
                    "balanceTokenOut": constraints.get("balanceTokenOut"),
                },
            )
        ]
