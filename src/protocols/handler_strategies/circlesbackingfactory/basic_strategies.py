from typing import Dict, Any, Optional
from src.protocols.handler_strategies.base import BaseStrategy
from src.framework.core.context import SimulationContext


class CreateLBPStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        
        
        
        params['personalCRC'] = None  # type: address
        
        
        
        
        
        params['personalCRCAmount'] = None  # type: uint256
        
        
        
        
        
        params['backingAsset'] = None  # type: address
        
        
        
        
        
        params['backingAssetAmount'] = None  # type: uint256
        
        
        

        return params


class ExitLBPStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        
        
        
        params['lbp'] = None  # type: address
        
        
        
        
        
        params['bptAmount'] = None  # type: uint256
        
        
        

        return params


class GetPersonalCirclesStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        
        
        
        params['avatar'] = None  # type: address
        
        
        

        return params


class NotifyReleaseStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        
        
        
        params['lbp'] = None  # type: address
        
        
        

        return params


class OnERC1155ReceivedStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        
        
        
        params['operator'] = None  # type: address
        
        
        
        
        
        params['from_'] = None  # type: address
        
        
        
        
        
        params['id'] = None  # type: uint256
        
        
        
        
        
        params['amount_value'] = None  # type: uint256 (renamed from 'value')
        
        
        
        
        
        params['data'] = None  # type: bytes
        
        
        

        return params


class SetReleaseTimestampStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        
        
        
        params['timestamp'] = None  # type: uint32
        
        
        

        return params


class SetSupportedBackingAssetStatusStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        
        
        
        params['backingAsset'] = None  # type: address
        
        
        
        
        
        params['status'] = None  # type: bool
        
        
        

        return params

