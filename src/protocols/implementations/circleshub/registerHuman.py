from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext
import random


@register_implementation("circleshub_registerHuman")
class CirclesHubRegisterHuman(BaseImplementation):
    """Implementation for registerHuman in CirclesHub"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate registerHuman call(s).

        Args:
            context: Current simulation context

                _inviter (address): Contract parameter

                _metadataDigest (bytes32): Contract parameter


        Returns:
            List[ContractCall]: List of calls to execute
        """
        client = context.get_client("circleshub")
        if not client:
            return []

        # Get constraints from profile
        constraints = context.agent.profile.get_action_config(
            "circleshub_registerHuman"
        ).constraints

        inviters = context.get_filtered_addresses(
            lambda addr: (client.isHuman(addr) or client.isGroup(addr)) and 
                        (client.balanceOf(addr, client.toTokenId(addr)) > 96e18),
            cache_key=f'potential_inviters'
        )
        if not inviters:
            return {}
        
        inviter = random.choice(inviters)
        

        unregistered_trusted = context.get_or_cache(
            f'unregistered_trusted_{inviter}',
            lambda: [
                addr for addr in context.agent_manager.address_to_agent.keys()
                if not client.isHuman(addr) and 
                not client.isGroup(addr) and 
                not client.isOrganization(addr) and 
                client.isTrusted(inviter, addr)
            ]
        )
        
        if not unregistered_trusted:
            return {}
        
        address = random.choice(unregistered_trusted)
        
        return [
            ContractCall(
                client_name="circleshub",
                method="registerHuman",
                params={
                    "sender": address,
                    "value": 0,
                    "_inviter": inviter,
                    "_metadataDigest": b"",
                },
            )
        ]
