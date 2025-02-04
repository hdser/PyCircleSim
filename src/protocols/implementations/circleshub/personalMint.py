from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("circleshub_personalMint")
class CirclesHubPersonalMint(BaseImplementation):
    """Implementation for personalMint in CirclesHub"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate personalMint call(s).

        Args:
            context: Current simulation context


        Returns:
            List[ContractCall]: List of calls to execute
        """
        sender = self.get_sender(context)
        if not sender:
            return []

        client = context.get_client("circleshub")
        if not client:
            return []


        return [
            ContractCall(
                client_name="circleshub",
                method="personalMint",
                params={
                    "sender": sender,
                    "value": 0,
                },
            )
        ]
