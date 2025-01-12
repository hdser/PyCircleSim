from typing import Dict, Any, Optional
from src.protocols.handler_strategies.base import BaseStrategy


class BurnStrategy(BaseStrategy):
    def get_params(self, agent, agent_manager, client, chain) -> Optional[Dict[str, Any]]:
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
    def get_params(self, agent, agent_manager, client, chain) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(agent)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'_human': None
            
        }


class GroupMintStrategy(BaseStrategy):
    def get_params(self, agent, agent_manager, client, chain) -> Optional[Dict[str, Any]]:
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
    def get_params(self, agent, agent_manager, client, chain) -> Optional[Dict[str, Any]]:
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
    def get_params(self, agent, agent_manager, client, chain) -> Optional[Dict[str, Any]]:
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
    def get_params(self, agent, agent_manager, client, chain) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(agent)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
        }


class RegisterCustomGroupStrategy(BaseStrategy):
    def get_params(self, agent, agent_manager, client, chain) -> Optional[Dict[str, Any]]:
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
    def get_params(self, agent, agent_manager, client, chain) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(agent)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'_mint': None
            
            ,'_name': None
            
            ,'_symbol': None
            
            ,'_metadataDigest': None
            
        }


class RegisterHumanStrategy(BaseStrategy):
    def get_params(self, agent, agent_manager, client, chain) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(agent)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'_inviter': None
            
            ,'_metadataDigest': None
            
        }


class RegisterOrganizationStrategy(BaseStrategy):
    def get_params(self, agent, agent_manager, client, chain) -> Optional[Dict[str, Any]]:
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
    def get_params(self, agent, agent_manager, client, chain) -> Optional[Dict[str, Any]]:
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
    def get_params(self, agent, agent_manager, client, chain) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(agent)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'_from': None
            
            ,'_to': None
            
            ,'_id': None
            
            ,'_value': None
            
            ,'_data': None
            
        }


class SetAdvancedUsageFlagStrategy(BaseStrategy):
    def get_params(self, agent, agent_manager, client, chain) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(agent)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'_flag': None
            
        }


class SetApprovalForAllStrategy(BaseStrategy):
    def get_params(self, agent, agent_manager, client, chain) -> Optional[Dict[str, Any]]:
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
    def get_params(self, agent, agent_manager, client, chain) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(agent)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
        }


class TrustStrategy(BaseStrategy):
    def get_params(self, agent, agent_manager, client, chain) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(agent)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'_trustReceiver': None
            
            ,'_expiry': None
            
        }


class WrapStrategy(BaseStrategy):
    def get_params(self, agent, agent_manager, client, chain) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(agent)
        if not sender:
            return None

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
            
