from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext


@register_implementation("circleshub_groupMint")
class CirclesHubGroupMint(BaseImplementation):
    """Implementation for groupMint in CirclesHub"""

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Generate groupMint call(s).

        Args:
            context: Current simulation context

                _group (address): Contract parameter

                _collateralAvatars (address[]): Contract parameter

                _amounts (uint256[]): Contract parameter

                _data (bytes): Contract parameter


        Returns:
            List[ContractCall]: List of calls to execute
        """
        client = context.get_client("circleshub")
        if not client:
            return []

        # Get constraints from profile
       # constraints = context.agent.profile.get_action_config(
       #     "circleshub_groupMint"
       # ).constraints

        groups = context.get_filtered_addresses(
            client.isGroup,
            cache_key='groups_list'
        )
        if not groups:
            return {}
        import random
        group = random.choice(groups)

        valid_senders = context.get_or_cache(
            f'valid_senders_for_{group}',
            lambda: [
                addr for addr in context.agent.accounts.keys()
                if client.isHuman(addr) and client.isTrusted(group, addr)
            ]
        )
        if not valid_senders:
            return None
        
        sender = random.choice(valid_senders)
        collateral_avatar = sender

        collateral_id = client.toTokenId(collateral_avatar)
        balance = client.balanceOf(collateral_avatar, collateral_id)
        if balance == 0:
            return {}

        amount = int(balance * random.uniform(0.1, 0.3))
        if amount == 0:
            return {}

        return [
            ContractCall(
                client_name="circleshub",
                method="groupMint",
                params={
                    "sender": sender,
                    "value": 0,
                    "_group": group,
                    "_collateralAvatars": [collateral_avatar],
                    "_amounts": [amount],
                    "_data": b"" ,
                },
            )
        ]
