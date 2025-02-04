from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("balancerv2vault_queryBatchSwap")
class BalancerV2VaultQueryBatchSwap(BaseImplementation):
    """Implementation for queryBatchSwap in BalancerV2Vault"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate queryBatchSwap call(s).

        Args:
            context: Current simulation context

                kind (uint8): Contract parameter

                swaps (tuple[]): Contract parameter

                assets (address[]): Contract parameter

                funds (tuple): Contract parameter


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
            "balancerv2vault_queryBatchSwap"
        ).constraints

        return [
            ContractCall(
                client_name="balancerv2vault",
                method="queryBatchSwap",
                params={
                    "sender": sender,
                    "value": 0,
                    "kind": constraints.get("kind"),
                    "swaps": constraints.get("swaps"),
                    "assets": constraints.get("assets"),
                    "funds": constraints.get("funds"),
                },
            )
        ]
