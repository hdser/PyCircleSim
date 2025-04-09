from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("circlesinflationaryerc20_permit")
class CirclesInflationaryERC20Permit(BaseImplementation):
    """Implementation for permit in CirclesInflationaryERC20"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate permit call(s).

        Args:
            context: Current simulation context

                _owner (address): Contract parameter

                _spender (address): Contract parameter

                _value (uint256): Contract parameter

                _deadline (uint256): Contract parameter

                _v (uint8): Contract parameter

                _r (bytes32): Contract parameter

                _s (bytes32): Contract parameter


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
            "circlesinflationaryerc20_permit"
        ).constraints

        return [
            ContractCall(
                client_name="circlesinflationaryerc20",
                method="permit",
                params={
                    "sender": sender,
                    "value": 0,
                    "_owner": constraints.get("_owner"),
                    "_spender": constraints.get("_spender"),
                    "_value": constraints.get("_value"),
                    "_deadline": constraints.get("_deadline"),
                    "_v": constraints.get("_v"),
                    "_r": constraints.get("_r"),
                    "_s": constraints.get("_s"),
                },
            )
        ]
