from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("balancerv2lbp_onExitPool")
class BalancerV2LBPOnExitPool(BaseImplementation):
    """Implementation for onExitPool in BalancerV2LBP"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate onExitPool call(s).

        Args:
            context: Current simulation context

                poolId (bytes32): Contract parameter

                sender (address): Contract parameter

                recipient (address): Contract parameter

                balances (uint256[]): Contract parameter

                lastChangeBlock (uint256): Contract parameter

                 (uint256): Contract parameter

                userData (bytes): Contract parameter


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
            "balancerv2lbp_onExitPool"
        ).constraints

        return [
            ContractCall(
                client_name="balancerv2lbp",
                method="onExitPool",
                params={
                    "sender": sender,
                    "value": 0,
                    "poolId": constraints.get("poolId"),
                    "sender": constraints.get("sender"),
                    "recipient": constraints.get("recipient"),
                    "balances": constraints.get("balances"),
                    "lastChangeBlock": constraints.get("lastChangeBlock"),
                    "": constraints.get(""),
                    "userData": constraints.get("userData"),
                },
            )
        ]
