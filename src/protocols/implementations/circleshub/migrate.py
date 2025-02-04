from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("circleshub_migrate")
class CirclesHubMigrate(BaseImplementation):
    """Implementation for migrate in CirclesHub"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate migrate call(s).

        Args:
            context: Current simulation context

                _owner (address): Contract parameter

                _avatars (address[]): Contract parameter

                _amounts (uint256[]): Contract parameter


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
            "circleshub_migrate"
        ).constraints

        return [
            ContractCall(
                client_name="circleshub",
                method="migrate",
                params={
                    "sender": sender,
                    "value": 0,
                    "_owner": constraints.get("_owner"),
                    "_avatars": constraints.get("_avatars"),
                    "_amounts": constraints.get("_amounts"),
                },
            )
        ]
