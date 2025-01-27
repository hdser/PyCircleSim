# src/protocols/handler_strategies/erc20/basic_strategies.py
from typing import Dict, Any, Optional
from src.protocols.handler_strategies.base import BaseStrategy
from src.framework.core.context import SimulationContext
import random

class ApproveStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Parameters must include token_address, spender, and amount
        params = {
            'sender': sender,
            'value': 0,
            'token_address': None,  # Must be set by caller
            'spender': None,       # Must be set by caller
            'amount': None         # Must be set by caller
        }
        
        return params

class TransferStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None

        # Get a random recipient from other addresses
        possible_recipients = [
            addr for addr in context.agent_manager.address_to_agent.keys()
            if addr != sender
        ]
        if not possible_recipients:
            return None
            
        recipient = random.choice(possible_recipients)
        
        params = {
            'sender': sender,
            'value': 0,
            'token_address': None,  # Must be set by caller
            'to': recipient,
            'amount': None         # Must be set by caller
        }
        
        return params

class TransferFromStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None

        # Get random from/to addresses excluding sender
        other_addresses = [
            addr for addr in context.agent_manager.address_to_agent.keys()
            if addr != sender
        ]
        if len(other_addresses) < 2:
            return None
            
        from_addr = random.choice(other_addresses)
        other_addresses.remove(from_addr)
        to_addr = random.choice(other_addresses)
        
        params = {
            'sender': sender,
            'value': 0,
            'token_address': None,  # Must be set by caller
            'from': from_addr,
            'to': to_addr,
            'amount': None         # Must be set by caller
        }
        
        return params

class BurnStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        params = {
            'sender': sender,
            'value': 0,
            'token_address': None,  # Must be set by caller
            'amount': None         # Must be set by caller
        }
        
        return params

class MintStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None

        # Get random recipient
        possible_recipients = list(context.agent_manager.address_to_agent.keys())
        if not possible_recipients:
            return None
            
        recipient = random.choice(possible_recipients)
        
        params = {
            'sender': sender,
            'value': 0,
            'token_address': None,  # Must be set by caller
            'to': recipient,
            'amount': None         # Must be set by caller
        }
        
        return params

class IncreaseAllowanceStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None

        # Get random spender
        possible_spenders = [
            addr for addr in context.agent_manager.address_to_agent.keys()
            if addr != sender
        ]
        if not possible_spenders:
            return None
            
        spender = random.choice(possible_spenders)
        
        params = {
            'sender': sender,
            'value': 0,
            'token_address': None,     # Must be set by caller
            'spender': spender,
            'added_value': None        # Must be set by caller
        }
        
        return params

class DecreaseAllowanceStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None

        # Get random spender
        possible_spenders = [
            addr for addr in context.agent_manager.address_to_agent.keys()
            if addr != sender
        ]
        if not possible_spenders:
            return None
            
        spender = random.choice(possible_spenders)
        
        params = {
            'sender': sender,
            'value': 0,
            'token_address': None,        # Must be set by caller
            'spender': spender,
            'subtracted_value': None      # Must be set by caller
        }
        
        return params