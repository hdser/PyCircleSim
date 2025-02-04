from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("balancerv2vault_exitPool")
class BalancerV2VaultExitPool(BaseImplementation):
    """Implementation for exitPool in BalancerV2Vault"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate exitPool call(s).

        Args:
            context: Current simulation context

                poolId (bytes32): Contract parameter

                sender (address): Contract parameter

                recipient (address): Contract parameter

                request (tuple): Contract parameter


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
            "balancerv2vault_exitPool"
        ).constraints

        return [
            ContractCall(
                client_name="balancerv2vault",
                method="exitPool",
                params={
                    "sender": sender,
                    "value": 0,
                    "poolId": constraints.get("poolId"),
                    "sender": constraints.get("sender"),
                    "recipient": constraints.get("recipient"),
                    "request": constraints.get("request"),
                },
            )
        ]
