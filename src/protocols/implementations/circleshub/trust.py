from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext
import random


@register_implementation("circleshub_trust")
class CirclesHubTrust(BaseImplementation):
    """Implementation for trust in CirclesHub"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate trust call(s).

        Args:
            context: Current simulation context

                _trustReceiver (address): Contract parameter

                _expiry (uint96): Contract parameter


        Returns:
            List[ContractCall]: List of calls to execute
        """
        sender = self.get_sender(context)
        if not sender:
            return []

        client = context.get_client("circleshub")
        if not client:
            return []

        # Get constraints from profile
        constraints = context.agent.profile.get_action_config(
            "circleshub_trust"
        ).constraints

        block_timestamp = context.chain.blocks.head.timestamp
        expiry_delta = 365 * 24 * 60 * 60
        expiry = int(block_timestamp + expiry_delta)

 
        trusters = context.get_filtered_addresses(
            lambda addr: client.isHuman(addr) or client.isGroup(addr),
            cache_key=f'potential_trusters'
        )
        if not trusters:
            return {}
        
        truster = random.choice(trusters)

        potential_trustees = context.get_or_cache(
            f'potential_trustees_{truster}',
            lambda: [
                addr for addr in context.agent_manager.address_to_agent.keys()
                if addr != truster and not client.isTrusted(truster, addr)
            ]
        )
        
        if not potential_trustees:
            return {}
        
        trustee = random.choice(potential_trustees)

        return [
            ContractCall(
                client_name="circleshub",
                method="trust",
                params={
                    "sender": sender,
                    "value": 0,
                    "_trustReceiver": trustee,
                    "_expiry": expiry,
                },
            )
        ]
