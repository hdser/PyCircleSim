from typing import Dict, Any, Optional
from eth_pydantic_types import HexBytes
import random
from src.protocols.handler_strategies.base import BaseStrategy


class BurnStrategy(BaseStrategy):
    def get_params(self, agent, client, chain) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(agent)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'_id': None
            
            ,'_amount': None
            
            ,'_data': None
            
        }


class CalculateIssuanceWithCheckStrategy(BaseStrategy):
    def get_params(self, agent, client, chain) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(agent)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'_human': None
            
        }


class GroupMintStrategy(BaseStrategy):
    def get_params(self, agent, client, chain) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(agent)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'_group': None
            
            ,'_collateralAvatars': None
            
            ,'_amounts': None
            
            ,'_data': None
            
        }


class MigrateStrategy(BaseStrategy):
    def get_params(self, agent, client, chain) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(agent)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'_owner': None
            
            ,'_avatars': None
            
            ,'_amounts': None
            
        }


class OperateFlowMatrixStrategy(BaseStrategy):
    def get_params(self, agent, client, chain) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(agent)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'_flowVertices': None
            
            ,'_flow': None
            
            ,'_streams': None
            
            ,'_packedCoordinates': None
            
        }


class PersonalMintStrategy(BaseStrategy):
    def get_params(self, agent, client, chain) -> Optional[Dict[str, Any]]:
        mintable_accounts = []
        for address in agent.accounts.keys():
            if client.isHuman(address) and not client.stopped(address):
                issuance, start_period, _ = client.calculateIssuance(address)
                if issuance != 0 and chain.blocks.head.timestamp >= start_period:
                    mintable_accounts.append(address)
        
        if not mintable_accounts:
            return {}
            
        return {
            'sender': random.choice(mintable_accounts)
        }


class RegisterCustomGroupStrategy(BaseStrategy):
    def get_params(self, agent, client, chain) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(agent)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'_mint': None
            
            ,'_treasury': None
            
            ,'_name': None
            
            ,'_symbol': None
            
            ,'_metadataDigest': None
            
        }


class RegisterGroupStrategy(BaseStrategy):
    def get_params(self, agent, client, chain) -> Optional[Dict[str, Any]]:
        group_number = getattr(agent, 'group_count', 0) + 1
        creator_address, _ = agent.create_account()
        return {
            'sender': creator_address,
            '_name': f"RingsGroup{creator_address[:4]}{group_number}",
            '_symbol': f"RG{creator_address[:2]}{group_number}",
            '_mint': "0x79Cbc9C7077dF161b92a745345A6Ade3fC626A60",
            '_metadataDigest': HexBytes("0x00")
        }


class RegisterHumanStrategy(BaseStrategy):
    def get_params(self, agent, client, chain) -> Optional[Dict[str, Any]]:
        if len(agent.accounts) < agent.profile.target_account_count:
            agent.create_account()

        unregistered = [addr for addr in agent.accounts.keys() 
                       if not client.isHuman(addr)]
        if not unregistered:
            return {}

        return {
            "sender": random.choice(unregistered),
            "_inviter": "0x0000000000000000000000000000000000000000",
            "_metadataDigest": HexBytes("0x00")
        }


class RegisterOrganizationStrategy(BaseStrategy):
    def get_params(self, agent, client, chain) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(agent)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'_name': None
            
            ,'_metadataDigest': None
            
        }


class SafeBatchTransferFromStrategy(BaseStrategy):
    def get_params(self, agent, client, chain) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(agent)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'_from': None
            
            ,'_to': None
            
            ,'_ids': None
            
            ,'_values': None
            
            ,'_data': None
            
        }


class SafeTransferFromStrategy(BaseStrategy):
    def get_params(self, agent, client, chain) -> Optional[Dict[str, Any]]:
        trusted_addresses = agent.state.get('trusted_addresses', set())
        if not trusted_addresses:
            return {}

        sender = self.get_sender(agent)
        if not sender:
            return {}

        receiver = random.choice(list(trusted_addresses))
        id = client.toTokenId(sender)
        balance = client.balanceOf(sender, id)

        if balance == 0:
            return {}

        amount = int(balance * random.uniform(0.1, 0.3))
        if amount == 0:
            return {}

        return {
            'sender': sender,
            '_from': sender,
            '_to': receiver,
            '_id': id,
            '_value': amount,
            '_data': b"",
        }


class SetAdvancedUsageFlagStrategy(BaseStrategy):
    def get_params(self, agent, client, chain) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(agent)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'_flag': None
            
        }


class SetApprovalForAllStrategy(BaseStrategy):
    def get_params(self, agent, client, chain) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(agent)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'_operator': None
            
            ,'_approved': None
            
        }


class StopStrategy(BaseStrategy):
    def get_params(self, agent, client, chain) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(agent)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
        }


class TrustStrategy(BaseStrategy):
    def get_params(self, agent, client, chain) -> Optional[Dict[str, Any]]:
        all_registered = set()
        truster = self.get_sender(agent)
        if not truster:
            return {}
            
        for addr in agent.accounts.keys():
            if client.isHuman(addr) and addr != truster:
                all_registered.add(addr)

        already_trusted = agent.state.get('trusted_addresses', set())
        potential_trustees = list(all_registered - already_trusted)
        
        if not potential_trustees:
            return {}

        trustee = random.choice(potential_trustees)
        expiry = int(chain.blocks.head.timestamp + 365 * 24 * 60 * 60)

        return {
            'sender': truster,
            '_trustReceiver': trustee,
            '_expiry': expiry,
        }


class WrapStrategy(BaseStrategy):
    def get_params(self, agent, client, chain) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(agent)
        if not sender:
            return {}
            
        id = client.toTokenId(sender) 
        balance = client.balanceOf(sender, id)
        if balance == 0:
            return {}
            
        return {
            "sender": sender,
            "_avatar": sender,
            "_amount": int(balance/10.0),
            "_type": 0
        }

