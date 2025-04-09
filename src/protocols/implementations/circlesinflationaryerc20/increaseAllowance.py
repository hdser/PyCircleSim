from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("circlesinflationaryerc20_increaseAllowance")
class CirclesInflationaryERC20IncreaseAllowance(BaseImplementation):
    """Implementation for increaseAllowance in CirclesInflationaryERC20"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate increaseAllowance call(s).

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

        client = context.get_client("circlesinflationaryerc20")
        if not client:
            return []

        # Get constraints from profile
        constraints = context.agent.profile.get_action_config(
            "circlesinflationaryerc20_increaseAllowance"
        ).constraints

        return [
            ContractCall(
                client_name="circlesinflationaryerc20",
                method="increaseAllowance",
                params={
                    "sender": sender,
                    "value": 0,
                    "_spender": constraints.get("_spender"),
                    "_addedValue": constraints.get("_addedValue"),
                },
            )
        ]
