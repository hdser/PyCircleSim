from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext
import random


@register_implementation("circleshub_registerGroup")
class CirclesHubRegisterGroup(BaseImplementation):
    """Implementation for registerGroup in CirclesHub"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate registerGroup call(s).

        Args:
            context: Current simulation context

                _mint (address): Contract parameter

                _name (string): Contract parameter

                _symbol (string): Contract parameter

                _metadataDigest (bytes32): Contract parameter


        Returns:
            List[ContractCall]: List of calls to execute
        """
        client = context.get_client("circleshub")
        if not client:
            return []

        # Get constraints from profile
        constraints = context.agent.profile.get_action_config(
            "circleshub_registerGroup"
        ).constraints

        unregistered = context.get_filtered_addresses(
            lambda addr: not (client.isHuman(addr) or client.isGroup(addr) or client.isOrganization(addr)),
            cache_key=f'unregistered_addresses_{context.agent.agent_id}'
        )
        if not unregistered:
            return {}
        
        creator_address = random.choice(unregistered)
        group_number = getattr(context.agent, 'group_count', 0) + 1
        mint_policy = constraints.get("MINT_POLICY","0x79Cbc9C7077dF161b92a745345A6Ade3fC626A60")

        
        return [
            ContractCall(
                client_name="circleshub",
                method="registerGroup",
                params={
                    "sender": creator_address,
                    "value": 0,
                    "_mint": mint_policy,
                    "_name": f"RingsGroup{creator_address[:4]}{group_number}",
                    "_symbol": f"RG{creator_address[:2]}{group_number}",
                    "_metadataDigest": b"",
                },
            )
        ]
