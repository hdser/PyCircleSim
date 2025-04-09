from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("circlesbackingfactory_createLBP")
class CirclesBackingFactoryCreateLBP(BaseImplementation):
    """Implementation for createLBP in CirclesBackingFactory"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate createLBP call(s).

        Args:
            context: Current simulation context

                personalCRC (address): Contract parameter

                personalCRCAmount (uint256): Contract parameter

                backingAsset (address): Contract parameter

                backingAssetAmount (uint256): Contract parameter


        Returns:
            List[ContractCall]: List of calls to execute
        """
        sender = self.get_sender(context)
        if not sender:
            return []

        client = context.get_client("circlesbackingfactory")
        if not client:
            return []

        # Get constraints from profile
        constraints = context.agent.profile.get_action_config(
            "circlesbackingfactory_createLBP"
        ).constraints

        return [
            ContractCall(
                client_name="circlesbackingfactory",
                method="createLBP",
                params={
                    "sender": sender,
                    "value": 0,
                    "personalCRC": constraints.get("personalCRC"),
                    "personalCRCAmount": constraints.get("personalCRCAmount"),
                    "backingAsset": constraints.get("backingAsset"),
                    "backingAssetAmount": constraints.get("backingAssetAmount"),
                },
            )
        ]
