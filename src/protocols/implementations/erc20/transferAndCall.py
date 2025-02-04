from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("erc20_transferAndCall")
class ERC20TransferAndCall(BaseImplementation):
    """Implementation for transferAndCall in erc20"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate transferAndCall call(s).

        Args:
            context: Current simulation context

                _to (address): Contract parameter

                _value (uint256): Contract parameter

                _data (bytes): Contract parameter


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
            "erc20_transferAndCall"
        ).constraints

        return [
            ContractCall(
                client_name="erc20",
                method="transferAndCall",
                params={
                    "sender": sender,
                    "value": 0,
                    "_to": constraints.get("_to"),
                    "_value": constraints.get("_value"),
                    "_data": constraints.get("_data"),
                },
            )
        ]
