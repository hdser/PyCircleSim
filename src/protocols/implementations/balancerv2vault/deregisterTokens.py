from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("balancerv2vault_deregisterTokens")
class BalancerV2VaultDeregisterTokens(BaseImplementation):
    """Implementation for deregisterTokens in BalancerV2Vault"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate deregisterTokens call(s).

        Args:
            context: Current simulation context

                poolId (bytes32): Contract parameter

                tokens (address[]): Contract parameter


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
            "balancerv2vault_deregisterTokens"
        ).constraints

        return [
            ContractCall(
                client_name="balancerv2vault",
                method="deregisterTokens",
                params={
                    "sender": sender,
                    "value": 0,
                    "poolId": constraints.get("poolId"),
                    "tokens": constraints.get("tokens"),
                },
            )
        ]
