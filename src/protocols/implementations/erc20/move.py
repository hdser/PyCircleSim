from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("erc20_move")
class ERC20Move(BaseImplementation):
    """Implementation for move in erc20"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate move call(s).

        Args:
            context: Current simulation context

                _from (address): Contract parameter

                _to (address): Contract parameter

                _amount (uint256): Contract parameter


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
        constraints = context.agent.profile.get_action_config("erc20_move").constraints

        return [
            ContractCall(
                client_name="erc20",
                method="move",
                params={
                    "sender": sender,
                    "value": 0,
                    "_from": constraints.get("_from"),
                    "_to": constraints.get("_to"),
                    "_amount": constraints.get("_amount"),
                },
            )
        ]
