from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("circlesbackingfactory_onERC1155Received")
class CirclesBackingFactoryOnERC1155Received(BaseImplementation):
    """Implementation for onERC1155Received in CirclesBackingFactory"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate onERC1155Received call(s).

        Args:
            context: Current simulation context

                operator (address): Contract parameter

                from (address): Contract parameter

                id (uint256): Contract parameter

                value (uint256): Contract parameter

                data (bytes): Contract parameter


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
            "circlesbackingfactory_onERC1155Received"
        ).constraints

        return [
            ContractCall(
                client_name="circlesbackingfactory",
                method="onERC1155Received",
                params={
                    "sender": sender,
                    "value": 0,
                    "operator": constraints.get("operator"),
                    "from": constraints.get("from"),
                    "id": constraints.get("id"),
                    "value": constraints.get("value"),
                    "data": constraints.get("data"),
                },
            )
        ]
