from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("erc20_transferFrom")
class ERC20TransferFrom(BaseImplementation):
    """Implementation for transferFrom in erc20"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate transferFrom call(s).

        Args:
            context: Current simulation context

                _sender (address): Contract parameter

                _recipient (address): Contract parameter

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
        constraints = context.agent.profile.get_action_config(
            "erc20_transferFrom"
        ).constraints

        return [
            ContractCall(
                client_name="erc20",
                method="transferFrom",
                params={
                    "sender": sender,
                    "value": 0,
                    "_sender": constraints.get("_sender"),
                    "_recipient": constraints.get("_recipient"),
                    "_amount": constraints.get("_amount"),
                },
            )
        ]
