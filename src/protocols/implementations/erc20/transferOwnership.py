from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("erc20_transferOwnership")
class ERC20TransferOwnership(BaseImplementation):
    """Implementation for transferOwnership in erc20"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate transferOwnership call(s).

        Args:
            context: Current simulation context

                _newOwner (address): Contract parameter


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
            "erc20_transferOwnership"
        ).constraints

        return [
            ContractCall(
                client_name="erc20",
                method="transferOwnership",
                params={
                    "sender": sender,
                    "value": 0,
                    "_newOwner": constraints.get("_newOwner"),
                },
            )
        ]
