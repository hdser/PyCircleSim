from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("supergroup_setup")
class SuperGroupSetup(BaseImplementation):
    """Implementation for setup in SuperGroup"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate setup call(s).

        Args:
            context: Current simulation context

                _owner (address): Contract parameter

                _service (address): Contract parameter

                _mintFee (uint256): Contract parameter

                _feeCollection (address): Contract parameter

                _redemptionBurnRate (uint256): Contract parameter

                _operators (address[]): Contract parameter

                _name (string): Contract parameter

                _symbol (string): Contract parameter

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
            "supergroup_setup"
        ).constraints

        return [
            ContractCall(
                client_name="supergroup",
                method="setup",
                params={
                    "sender": sender,
                    "value": 0,
                    "_owner": constraints.get("_owner"),
                    "_service": constraints.get("_service"),
                    "_mintFee": constraints.get("_mintFee"),
                    "_feeCollection": constraints.get("_feeCollection"),
                    "_redemptionBurnRate": constraints.get("_redemptionBurnRate"),
                    "_operators": constraints.get("_operators"),
                    "_name": constraints.get("_name"),
                    "_symbol": constraints.get("_symbol"),
                    "_metadataDigest": constraints.get("_metadataDigest"),
                },
            )
        ]
