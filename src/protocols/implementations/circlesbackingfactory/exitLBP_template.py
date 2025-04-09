from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("circlesbackingfactory_exitLBP")
class CirclesBackingFactoryExitLBP(BaseImplementation):
    """Implementation for exitLBP in CirclesBackingFactory"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate exitLBP call(s).

        Args:
            context: Current simulation context

                lbp (address): Contract parameter

                bptAmount (uint256): Contract parameter


        Returns:
            List[ContractCall]: List of calls to execute
        """
        sender = self.get_sender(context)
        if not sender:
            return []

        client = context.get_client("circlesbackingfactory")
        if not client:
            return []

        # Get constraints from profile
        constraints = context.agent.profile.get_action_config(
            "circlesbackingfactory_exitLBP"
        ).constraints

        return [
            ContractCall(
                client_name="circlesbackingfactory",
                method="exitLBP",
                params={
                    "sender": sender,
                    "value": 0,
                    "lbp": constraints.get("lbp"),
                    "bptAmount": constraints.get("bptAmount"),
                },
            )
        ]
