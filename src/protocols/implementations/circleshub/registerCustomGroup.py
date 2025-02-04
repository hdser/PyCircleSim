from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("circleshub_registerCustomGroup")
class CirclesHubRegisterCustomGroup(BaseImplementation):
    """Implementation for registerCustomGroup in CirclesHub"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate registerCustomGroup call(s).

        Args:
            context: Current simulation context

                _mint (address): Contract parameter

                _treasury (address): Contract parameter

                _name (string): Contract parameter

                _symbol (string): Contract parameter

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
            "circleshub_registerCustomGroup"
        ).constraints

        return [
            ContractCall(
                client_name="circleshub",
                method="registerCustomGroup",
                params={
                    "sender": sender,
                    "value": 0,
                    "_mint": constraints.get("_mint"),
                    "_treasury": constraints.get("_treasury"),
                    "_name": constraints.get("_name"),
                    "_symbol": constraints.get("_symbol"),
                    "_metadataDigest": constraints.get("_metadataDigest"),
                },
            )
        ]
