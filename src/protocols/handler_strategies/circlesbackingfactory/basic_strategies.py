from typing import Dict, Any, Optional
from src.protocols.handler_strategies.base import BaseStrategy
from src.framework.core.context import SimulationContext


class CreateLBPStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'personalCRC': None
            
            ,'personalCRCAmount': None
            
            ,'backingAsset': None
            
            ,'backingAssetAmount': None
            
        }


class ExitLBPStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'lbp': None
            
            ,'bptAmount': None
            
        }


class GetPersonalCirclesStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'avatar': None
            
        }


class OnERC1155ReceivedStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'operator': None
            
            ,'from_': None
            
            ,'id': None
            
            ,'value': None
            
            ,'data': None
            
        }


class SetReleaseTimestampStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'timestamp': None
            
        }


class SetSupportedBackingAssetStatusStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        return {
            'sender': sender,
            'value': 0
            
            ,'backingAsset': None
            
            ,'status': None
            
        }

