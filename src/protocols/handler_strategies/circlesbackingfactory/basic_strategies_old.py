from typing import Dict, Any, Optional
from src.protocols.handler_strategies.base import BaseStrategy
from src.framework.core.context import SimulationContext


class CreateLBPStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return {}
            
        client_hub = context.get_client('circleshub')

        if not client_hub:
            return {}
        
        if not client_hub.isHuman(sender) and not client_hub.isGroup(sender):
            return {}
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
        constraints = context.agent.profile.action_configs['circlesbackingfactory_CreateLBP'].constraints
        
        is_set = False
        for constraint in constraints: 
            print(constraint)
            if 'backingAsset' in constraint:
                is_set = True 
                params['backingAsset'] = constraint['backingAsset']

        if not is_set:
            return {}
        

        params['personalCRC'] = '0xf81c47609e19b1456ddc6acb730f8f5b64840429'  # type: address
        params['personalCRCAmount'] = 10000000000000000000  # type: uint256
        #params['backingAsset'] = constraints['backingAsset']   # type: address
        params['backingAssetAmount'] = 10000000000000000  # type: uint256
        
        print(params)
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

