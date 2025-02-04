from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("erc20_finishMinting")
class ERC20FinishMinting(BaseImplementation):
    """Implementation for finishMinting in erc20"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate finishMinting call(s).

        Args:
            context: Current simulation context


        Returns:
            List[ContractCall]: List of calls to execute
        """
        sender = self.get_sender(context)
        if not sender:
            return []

        client = context.get_client("erc20")
        if not client:
            return []

        # Get constraints from profile
        constraints = context.agent.profile.get_action_config(
            "erc20_finishMinting"
        ).constraints

        return [
            ContractCall(
                client_name="erc20",
                method="finishMinting",
                params={
                    "sender": sender,
                    "value": 0,
                },
            )
        ]
