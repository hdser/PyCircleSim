from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("balancerv2lbp_setPaused")
class BalancerV2LBPSetPaused(BaseImplementation):
    """Implementation for setPaused in BalancerV2LBP"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate setPaused call(s).

        Args:
            context: Current simulation context

                paused (bool): Contract parameter


        Returns:
            List[ContractCall]: List of calls to execute
        """
        sender = self.get_sender(context)
        if not sender:
            return []

        client = context.get_client("balancerv2lbp")
        if not client:
            return []

        # Get constraints from profile
        constraints = context.agent.profile.get_action_config(
            "balancerv2lbp_setPaused"
        ).constraints

        return [
            ContractCall(
                client_name="balancerv2lbp",
                method="setPaused",
                params={
                    "sender": sender,
                    "value": 0,
                    "paused": constraints.get("paused"),
                },
            )
        ]
