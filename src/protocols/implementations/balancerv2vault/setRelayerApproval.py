from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("balancerv2vault_setRelayerApproval")
class BalancerV2VaultSetRelayerApproval(BaseImplementation):
    """Implementation for setRelayerApproval in BalancerV2Vault"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate setRelayerApproval call(s).

        Args:
            context: Current simulation context

                sender (address): Contract parameter

                relayer (address): Contract parameter

                approved (bool): Contract parameter


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
            "balancerv2vault_setRelayerApproval"
        ).constraints

        return [
            ContractCall(
                client_name="balancerv2vault",
                method="setRelayerApproval",
                params={
                    "sender": sender,
                    "value": 0,
                    "sender": constraints.get("sender"),
                    "relayer": constraints.get("relayer"),
                    "approved": constraints.get("approved"),
                },
            )
        ]
