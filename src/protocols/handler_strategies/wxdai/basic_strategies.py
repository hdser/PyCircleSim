from typing import Dict, Any, Optional
from src.protocols.handler_strategies.base import BaseStrategy


class ApproveStrategy(BaseStrategy):
    def get_params(self, agent, agent_manager, client, chain) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(agent)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'guy': None
            
            ,'wad': None
            
        }


class TransferFromStrategy(BaseStrategy):
    def get_params(self, agent, agent_manager, client, chain) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(agent)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'src': None
            
            ,'dst': None
            
            ,'wad': None
            
        }


class WithdrawStrategy(BaseStrategy):
    def get_params(self, agent, agent_manager, client, chain) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(agent)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'wad': None
            
        }


class TransferStrategy(BaseStrategy):
    def get_params(self, agent, agent_manager, client, chain) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(agent)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'dst': None
            
            ,'wad': None
            
        }


class DepositStrategy(BaseStrategy):
    def get_params(self, agent, agent_manager, client, chain) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(agent)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': int(10**18)
            
        }

