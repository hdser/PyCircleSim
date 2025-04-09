from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("supergroup_onERC1155BatchReceived")
class SuperGroupOnERC1155BatchReceived(BaseImplementation):
    """Implementation for onERC1155BatchReceived in SuperGroup"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate onERC1155BatchReceived call(s).

        Args:
            context: Current simulation context

                 (address): Contract parameter

                _from (address): Contract parameter

                _ids (uint256[]): Contract parameter

                _values (uint256[]): Contract parameter

                _data (bytes): Contract parameter


        Returns:
            List[ContractCall]: List of calls to execute
        """
        sender = self.get_sender(context)
        if not sender:
            return []

        client = context.get_client("supergroup")
        if not client:
            return []

        # Get constraints from profile
        constraints = context.agent.profile.get_action_config(
            "supergroup_onERC1155BatchReceived"
        ).constraints

        return [
            ContractCall(
                client_name="supergroup",
                method="onERC1155BatchReceived",
                params={
                    "sender": sender,
                    "value": 0,
                    "": constraints.get(""),
                    "_from": constraints.get("_from"),
                    "_ids": constraints.get("_ids"),
                    "_values": constraints.get("_values"),
                    "_data": constraints.get("_data"),
                },
            )
        ]
