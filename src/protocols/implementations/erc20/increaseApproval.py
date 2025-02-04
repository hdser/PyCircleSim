from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("erc20_increaseApproval")
class ERC20IncreaseApproval(BaseImplementation):
    """Implementation for increaseApproval in erc20"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate increaseApproval call(s).

        Args:
            context: Current simulation context

                _spender (address): Contract parameter

                _addedValue (uint256): Contract parameter


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
            "erc20_increaseApproval"
        ).constraints

        return [
            ContractCall(
                client_name="erc20",
                method="increaseApproval",
                params={
                    "sender": sender,
                    "value": 0,
                    "_spender": constraints.get("_spender"),
                    "_addedValue": constraints.get("_addedValue"),
                },
            )
        ]
