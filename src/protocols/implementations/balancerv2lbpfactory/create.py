from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("balancerv2lbpfactory_create")
class BalancerV2LBPFactoryCreate(BaseImplementation):
    """Implementation for create in BalancerV2LBPFactory"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate create call(s).

        Args:
            context: Current simulation context

                name (string): Contract parameter

                symbol (string): Contract parameter

                tokens (address[]): Contract parameter

                weights (uint256[]): Contract parameter

                swapFeePercentage (uint256): Contract parameter

                owner (address): Contract parameter

                swapEnabledOnStart (bool): Contract parameter


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
            "balancerv2lbpfactory_create"
        ).constraints

        return [
            ContractCall(
                client_name="balancerv2lbpfactory",
                method="create",
                params={
                    "sender": sender,
                    "value": 0,
                    "name": constraints.get("name"),
                    "symbol": constraints.get("symbol"),
                    "tokens": constraints.get("tokens"),
                    "weights": constraints.get("weights"),
                    "swapFeePercentage": constraints.get("swapFeePercentage"),
                    "owner": constraints.get("owner"),
                    "swapEnabledOnStart": constraints.get("swapEnabledOnStart"),
                },
            )
        ]
