import random
from typing import Dict, Any
from eth_pydantic_types import HexBytes
from ..base import BaseStrategy

class SybilRegisterHumanStrategy(BaseStrategy):
    """Sybil variant that always creates new accounts"""
    def get_params(self, agent, client, chain) -> Dict[str, Any]:
        # Create max accounts possible for sybil behavior
        if len(agent.accounts) >= agent.profile.target_account_count:
            return {}
            
        address, _ = agent.create_account()
        return {
            "sender": address,
            "_inviter": "0x0000000000000000000000000000000000000000",
            "_metadataDigest": HexBytes("0x00")
        }

class SybilPersonalMintStrategy(BaseStrategy):
    """Sybil variant that aggressively mints with all accounts"""
    def get_params(self, agent, client, chain) -> Dict[str, Any]:
        # Try all accounts in order to mint as much as possible
        for address in agent.accounts.keys():
            if client.isHuman(address) and not client.stopped(address):
                issuance, start_period, _ = client.calculateIssuance(address)
                if issuance != 0 and chain.blocks.head.timestamp >= start_period:
                    return {'sender': address}
        return {}

class SybilTrustStrategy(BaseStrategy):
    """Sybil variant that creates dense trust network between own accounts"""
    def get_params(self, agent, client, chain) -> Dict[str, Any]:
        own_accounts = list(agent.accounts.keys())
        if len(own_accounts) < 2:
            return {}
            
        # Create dense trust network between own accounts
        truster = random.choice(own_accounts)
        trustee = random.choice([a for a in own_accounts if a != truster])
        expiry = int(chain.blocks.head.timestamp + 2 * 365 * 24 * 60 * 60)  # 2 years

        return {
            'sender': truster,
            '_trustReceiver': trustee,
            '_expiry': expiry
        }

class SybilGroupStrategy(BaseStrategy):
    """Sybil variant creating multiple groups"""
    def get_params(self, agent, client, chain) -> Dict[str, Any]:
        creator_address, _ = agent.create_account()
        group_number = len(agent.state.get('isGroup', [])) + 1
        
        group_name = f"SybilGroup{creator_address[:4]}{group_number}"
        group_symbol = f"SG{creator_address[:2]}{group_number}"

        mint_policy = "0x79Cbc9C7077dF161b92a745345A6Ade3fC626A60"
        
        return {
            'sender': creator_address,
            '_name': group_name,
            '_symbol': group_symbol,
            '_mint': mint_policy,
            '_metadataDigest': HexBytes("0x00")
        }

class SybilTransferStrategy(BaseStrategy):
    """Sybil variant doing high frequency transfers between own accounts"""
    def get_params(self, agent, client, chain) -> Dict[str, Any]:
        own_accounts = list(agent.accounts.keys())
        if len(own_accounts) < 2:
            return {}

        sender = random.choice(own_accounts)
        receiver = random.choice([a for a in own_accounts if a != sender])
        
        id = client.toTokenId(sender)
        balance = client.balanceOf(sender, id)

        if balance == 0:
            return {}
            
        # Transfer larger portions in sybil pattern
        amount = int(balance * random.uniform(0.4, 0.8))
        
        return {
            'sender': sender,
            '_from': sender,
            '_to': receiver,
            '_id': id,
            '_value': amount,
            '_data': b"",
        }