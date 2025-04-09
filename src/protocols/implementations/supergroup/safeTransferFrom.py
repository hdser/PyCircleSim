from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("supergroup_safeTransferFrom")
class SuperGroupSafeTransferFrom(BaseImplementation):
    """Implementation for safeTransferFrom in SuperGroup"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate safeTransferFrom call(s).

        Args:
            context: Current simulation context

                _from (address): Contract parameter

                _to (address): Contract parameter

                _id (uint256): Contract parameter

                _value (uint256): Contract parameter

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
            "supergroup_safeTransferFrom"
        ).constraints

        return [
            ContractCall(
                client_name="supergroup",
                method="safeTransferFrom",
                params={
                    "sender": sender,
                    "value": 0,
                    "_from": constraints.get("_from"),
                    "_to": constraints.get("_to"),
                    "_id": constraints.get("_id"),
                    "_value": constraints.get("_value"),
                    "_data": constraints.get("_data"),
                },
            )
        ]
