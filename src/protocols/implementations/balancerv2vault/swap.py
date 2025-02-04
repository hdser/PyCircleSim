from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("balancerv2vault_swap")
class BalancerV2VaultSwap(BaseImplementation):
    """Implementation for swap in BalancerV2Vault"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate swap call(s).

        Args:
            context: Current simulation context

                singleSwap (tuple): Contract parameter

                funds (tuple): Contract parameter

                limit (uint256): Contract parameter

                deadline (uint256): Contract parameter


        Returns:
            List[ContractCall]: List of calls to execute
        """
        sender = self.get_sender(context)
        if not sender:
            return []

        client = context.get_client("balancerv2vault")
        if not client:
            return []

        # Get constraints from profile
        constraints = context.agent.profile.get_action_config(
            "balancerv2vault_swap"
        ).constraints

        return [
            ContractCall(
                client_name="balancerv2vault",
                method="swap",
                params={
                    "sender": sender,
                    "value": 0,
                    "singleSwap": constraints.get("singleSwap"),
                    "funds": constraints.get("funds"),
                    "limit": constraints.get("limit"),
                    "deadline": constraints.get("deadline"),
                },
            )
        ]
