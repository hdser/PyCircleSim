from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("circleserc20lift_ensureERC20")
class CirclesERC20LiftEnsureERC20(BaseImplementation):
    """Implementation for ensureERC20 in CirclesERC20Lift"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate ensureERC20 call(s).

        Args:
            context: Current simulation context

                _avatar (address): Contract parameter

                _circlesType (uint8): Contract parameter


        Returns:
            List[ContractCall]: List of calls to execute
        """
        sender = self.get_sender(context)
        if not sender:
            return []

        client = context.get_client("circleserc20lift")
        if not client:
            return []

        # Get constraints from profile
        constraints = context.agent.profile.get_action_config(
            "circleserc20lift_ensureERC20"
        ).constraints

        return [
            ContractCall(
                client_name="circleserc20lift",
                method="ensureERC20",
                params={
                    "sender": sender,
                    "value": 0,
                    "_avatar": sender,
                    "_circlesType": constraints.get("_circlesType"),
                },
            )
        ]
