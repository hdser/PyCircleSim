from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("supergroup_registerOperatorRequest")
class SuperGroupRegisterOperatorRequest(BaseImplementation):
    """Implementation for registerOperatorRequest in SuperGroup"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate registerOperatorRequest call(s).

        Args:
            context: Current simulation context

                _minter (address): Contract parameter

                _group (address): Contract parameter

                _collateral (uint256[]): Contract parameter

                _amounts (uint256[]): Contract parameter


        Returns:
            List[ContractCall]: List of calls to execute
        """
        sender = self.get_sender(context)
        if not sender:
            return []

        client = context.get_client("supergroup")
        if not client:
            return []

        # Get constraints from profile
        constraints = context.agent.profile.get_action_config(
            "supergroup_registerOperatorRequest"
        ).constraints

        return [
            ContractCall(
                client_name="supergroup",
                method="registerOperatorRequest",
                params={
                    "sender": sender,
                    "value": 0,
                    "_minter": constraints.get("_minter"),
                    "_group": constraints.get("_group"),
                    "_collateral": constraints.get("_collateral"),
                    "_amounts": constraints.get("_amounts"),
                },
            )
        ]
