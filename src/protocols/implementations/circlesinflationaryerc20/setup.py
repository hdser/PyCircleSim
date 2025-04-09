from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("circlesinflationaryerc20_setup")
class CirclesInflationaryERC20Setup(BaseImplementation):
    """Implementation for setup in CirclesInflationaryERC20"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate setup call(s).

        Args:
            context: Current simulation context

                _hub (address): Contract parameter

                _nameRegistry (address): Contract parameter

                _avatar (address): Contract parameter


        Returns:
            List[ContractCall]: List of calls to execute
        """
        sender = self.get_sender(context)
        if not sender:
            return []

        client = context.get_client("circlesinflationaryerc20")
        if not client:
            return []

        # Get constraints from profile
        constraints = context.agent.profile.get_action_config(
            "circlesinflationaryerc20_setup"
        ).constraints

        return [
            ContractCall(
                client_name="circlesinflationaryerc20",
                method="setup",
                params={
                    "sender": sender,
                    "value": 0,
                    "_hub": constraints.get("_hub"),
                    "_nameRegistry": constraints.get("_nameRegistry"),
                    "_avatar": constraints.get("_avatar"),
                },
            )
        ]
