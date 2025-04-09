from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("balancerv2lbp_permit")
class BalancerV2LBPPermit(BaseImplementation):
    """Implementation for permit in BalancerV2LBP"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate permit call(s).

        Args:
            context: Current simulation context

                owner (address): Contract parameter

                spender (address): Contract parameter

                value (uint256): Contract parameter

                deadline (uint256): Contract parameter

                v (uint8): Contract parameter

                r (bytes32): Contract parameter

                s (bytes32): Contract parameter


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
            "balancerv2lbp_permit"
        ).constraints

        return [
            ContractCall(
                client_name="balancerv2lbp",
                method="permit",
                params={
                    "sender": sender,
                    "value": 0,
                    "owner": constraints.get("owner"),
                    "spender": constraints.get("spender"),
                    "value": constraints.get("value"),
                    "deadline": constraints.get("deadline"),
                    "v": constraints.get("v"),
                    "r": constraints.get("r"),
                    "s": constraints.get("s"),
                },
            )
        ]
