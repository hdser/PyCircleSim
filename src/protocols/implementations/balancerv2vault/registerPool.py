from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("balancerv2vault_registerPool")
class BalancerV2VaultRegisterPool(BaseImplementation):
    """Implementation for registerPool in BalancerV2Vault"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate registerPool call(s).

        Args:
            context: Current simulation context

                specialization (uint8): Contract parameter


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
            "balancerv2vault_registerPool"
        ).constraints

        return [
            ContractCall(
                client_name="balancerv2vault",
                method="registerPool",
                params={
                    "sender": sender,
                    "value": 0,
                    "specialization": constraints.get("specialization"),
                },
            )
        ]
