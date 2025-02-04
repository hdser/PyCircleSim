from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("erc20_decreaseAllowance")
class ERC20DecreaseAllowance(BaseImplementation):
    """Implementation for decreaseAllowance in erc20"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate decreaseAllowance call(s).

        Args:
            context: Current simulation context

                spender (address): Contract parameter

                subtractedValue (uint256): Contract parameter


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
            "erc20_decreaseAllowance"
        ).constraints

        return [
            ContractCall(
                client_name="erc20",
                method="decreaseAllowance",
                params={
                    "sender": sender,
                    "value": 0,
                    "spender": constraints.get("spender"),
                    "subtractedValue": constraints.get("subtractedValue"),
                },
            )
        ]
