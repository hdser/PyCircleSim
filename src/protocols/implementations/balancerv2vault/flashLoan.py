from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("balancerv2vault_flashLoan")
class BalancerV2VaultFlashLoan(BaseImplementation):
    """Implementation for flashLoan in BalancerV2Vault"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate flashLoan call(s).

        Args:
            context: Current simulation context

                recipient (address): Contract parameter

                tokens (address[]): Contract parameter

                amounts (uint256[]): Contract parameter

                userData (bytes): Contract parameter


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
            "balancerv2vault_flashLoan"
        ).constraints

        return [
            ContractCall(
                client_name="balancerv2vault",
                method="flashLoan",
                params={
                    "sender": sender,
                    "value": 0,
                    "recipient": constraints.get("recipient"),
                    "tokens": constraints.get("tokens"),
                    "amounts": constraints.get("amounts"),
                    "userData": constraints.get("userData"),
                },
            )
        ]
