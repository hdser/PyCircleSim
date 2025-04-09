from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("supergroup_updateMetadataDigest")
class SuperGroupUpdateMetadataDigest(BaseImplementation):
    """Implementation for updateMetadataDigest in SuperGroup"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate updateMetadataDigest call(s).

        Args:
            context: Current simulation context

                _metadataDigest (bytes32): Contract parameter


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
            "supergroup_updateMetadataDigest"
        ).constraints

        return [
            ContractCall(
                client_name="supergroup",
                method="updateMetadataDigest",
                params={
                    "sender": sender,
                    "value": 0,
                    "_metadataDigest": constraints.get("_metadataDigest"),
                },
            )
        ]
