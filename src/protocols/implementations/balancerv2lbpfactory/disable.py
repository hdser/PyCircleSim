from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("balancerv2lbpfactory_disable")
class BalancerV2LBPFactoryDisable(BaseImplementation):
    """Implementation for disable in BalancerV2LBPFactory"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate disable call(s).

        Args:
            context: Current simulation context


        Returns:
            List[ContractCall]: List of calls to execute
        """
        sender = self.get_sender(context)
        if not sender:
            return []

        client = context.get_client("balancerv2lbpfactory")
        if not client:
            return []

        # Get constraints from profile
        constraints = context.agent.profile.get_action_config(
            "balancerv2lbpfactory_disable"
        ).constraints

        return [
            ContractCall(
                client_name="balancerv2lbpfactory",
                method="disable",
                params={
                    "sender": sender,
                    "value": 0,
                },
            )
        ]
