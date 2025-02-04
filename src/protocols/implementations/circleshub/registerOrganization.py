from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("circleshub_registerOrganization")
class CirclesHubRegisterOrganization(BaseImplementation):
    """Implementation for registerOrganization in CirclesHub"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate registerOrganization call(s).

        Args:
            context: Current simulation context

                _name (string): Contract parameter

                _metadataDigest (bytes32): Contract parameter


        Returns:
            List[ContractCall]: List of calls to execute
        """
        sender = self.get_sender(context)
        if not sender:
            return []

        client = context.get_client("circleshub")
        if not client:
            return []

        # Get constraints from profile
        constraints = context.agent.profile.get_action_config(
            "circleshub_registerOrganization"
        ).constraints

        return [
            ContractCall(
                client_name="circleshub",
                method="registerOrganization",
                params={
                    "sender": sender,
                    "value": 0,
                    "_name": constraints.get("_name"),
                    "_metadataDigest": constraints.get("_metadataDigest"),
                },
            )
        ]
