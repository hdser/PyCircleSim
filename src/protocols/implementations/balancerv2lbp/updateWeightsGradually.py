from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("balancerv2lbp_updateWeightsGradually")
class BalancerV2LBPUpdateWeightsGradually(BaseImplementation):
    """Implementation for updateWeightsGradually in BalancerV2LBP"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate updateWeightsGradually call(s).

        Args:
            context: Current simulation context

                startTime (uint256): Contract parameter

                endTime (uint256): Contract parameter

                endWeights (uint256[]): Contract parameter


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
            "balancerv2lbp_updateWeightsGradually"
        ).constraints

        return [
            ContractCall(
                client_name="balancerv2lbp",
                method="updateWeightsGradually",
                params={
                    "sender": sender,
                    "value": 0,
                    "startTime": constraints.get("startTime"),
                    "endTime": constraints.get("endTime"),
                    "endWeights": constraints.get("endWeights"),
                },
            )
        ]
