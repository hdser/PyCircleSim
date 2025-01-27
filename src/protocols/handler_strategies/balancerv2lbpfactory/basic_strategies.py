from typing import Dict, Any, Optional
from src.protocols.handler_strategies.base import BaseStrategy
from src.framework.core.context import SimulationContext


class CreateStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        name = 'Test Pool'
        symbol = 'TP'
        crc20 = '0x330941027d6fcd7e28ccb7ad2e15275af29f9ad8'
        backingAsset = '0x6A023CCd1ff6F2045C3309768eAd9E68F978f6e1'
        weight1 = 10000000000000000
        weight99 = 990000000000000000

        tokens = []
        tokens.append(crc20 if crc20 < backingAsset else backingAsset)
        tokens.append(backingAsset if crc20 < backingAsset else crc20)
        
        weights = []
        weights.append(weight1 if crc20 < backingAsset else weight99)
        weights.append(weight99 if crc20 < backingAsset else weight1)

        swapFeePercentage = 10000000000000000
        owner = sender
        swapEnabledOnStart = True
        
        params['name'] = name  # type: string
        params['symbol'] = symbol  # type: string
        params['tokens'] = tokens  # type: address[]
        params['weights'] = weights  # type: uint256[]
        params['swapFeePercentage'] = swapFeePercentage  # type: uint256
        params['owner'] = owner  # type: address
        params['swapEnabledOnStart'] = swapEnabledOnStart  # type: bool
        

        return params


class DisableStrategy(BaseStrategy):
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        # Initialize parameters with transaction details
        params = {
            'sender': sender,     # Transaction sender
            'value': 0            # Transaction value
        }
            
        

        return params

