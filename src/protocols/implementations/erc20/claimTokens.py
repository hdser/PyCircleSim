from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("erc20_claimTokens")
class ERC20ClaimTokens(BaseImplementation):
    """Implementation for claimTokens in erc20"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate claimTokens call(s).

        Args:
            context: Current simulation context

                _token (address): Contract parameter

                _to (address): Contract parameter


        Returns:
            List[ContractCall]: List of calls to execute
        """
        sender = self.get_sender(context)
        if not sender:
            return []

        client = context.get_client("erc20")
        if not client:
            return []

        # Get constraints from profile
        constraints = context.agent.profile.get_action_config(
            "erc20_claimTokens"
        ).constraints

        return [
            ContractCall(
                client_name="erc20",
                method="claimTokens",
                params={
                    "sender": sender,
                    "value": 0,
                    "_token": constraints.get("_token"),
                    "_to": constraints.get("_to"),
                },
            )
        ]
