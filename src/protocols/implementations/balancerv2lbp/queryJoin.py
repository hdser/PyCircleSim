from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("balancerv2lbp_queryJoin")
class BalancerV2LBPQueryJoin(BaseImplementation):
    """Implementation for queryJoin in BalancerV2LBP"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate queryJoin call(s).

        Args:
            context: Current simulation context

                poolId (bytes32): Contract parameter

                sender (address): Contract parameter

                recipient (address): Contract parameter

                balances (uint256[]): Contract parameter

                lastChangeBlock (uint256): Contract parameter

                protocolSwapFeePercentage (uint256): Contract parameter

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
            "balancerv2lbp_queryJoin"
        ).constraints

        return [
            ContractCall(
                client_name="balancerv2lbp",
                method="queryJoin",
                params={
                    "sender": sender,
                    "value": 0,
                    "poolId": constraints.get("poolId"),
                    "sender": constraints.get("sender"),
                    "recipient": constraints.get("recipient"),
                    "balances": constraints.get("balances"),
                    "lastChangeBlock": constraints.get("lastChangeBlock"),
                    "protocolSwapFeePercentage": constraints.get(
                        "protocolSwapFeePercentage"
                    ),
                    "userData": constraints.get("userData"),
                },
            )
        ]
