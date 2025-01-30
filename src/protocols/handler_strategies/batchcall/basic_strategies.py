from typing import Dict, Any, Optional
from src.protocols.handler_strategies.base import BaseStrategy
from src.framework.core import SimulationContext
from src.framework.logging import get_logger
import random

logger = get_logger(__name__)

class DepositAndSwapStrategy(BaseStrategy):
    """Strategy for depositing xDAI and swapping on Balancer"""
    
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        value = int(10e18)  # 10 xDAI
        VAULT = '0xBA12222222228d8Ba445958a75a0704d566BF2C8'
        WXDAI = '0xe91d153e0b41518a2ce8dd3d7944fa863463a97d'  # WxDAI
        BACKING_ASSET = '0x6A023CCd1ff6F2045C3309768eAd9E68F978f6e1'   # WETH
        CIRCLES_HUB = '0xc12C1E50ABB450d6205Ea2C3Fa861b3B834d13e8' 

        batch_calls = []

        # 1) xDAI deposit operation
        #_____________________________________
        batch_calls.append({
            'client_name': 'wxdai',
            'method': 'deposit',
            'params': {
                'sender': sender,
                'value': value
            }
        })

        # 2) Set WxDAI approval from VAULT
        #_____________________________________
        batch_calls.append({
            'client_name': 'erc20',
            'method': 'approve', 
            'params': {
                'token_address': WXDAI,
                'spender': VAULT,
                'amount': value * 2, 
                'sender': sender,
                'value': 0
            }
        })

        # 3) Swap WxDAI to Token
        #_____________________________________
        path = context.find_swap_path(WXDAI, BACKING_ASSET)
        if not path:
            logger.warning(f"No path found between {WXDAI} and {BACKING_ASSET}")
            return None

        # Build assets array ensuring proper case
        assets = [WXDAI.lower()]
        for hop in path:
            if hop['to_token'] not in assets:
                assets.append(hop['to_token'])
        logger.debug(f"Assets array: {assets}")

        # Build swaps array
        swaps = []
        for i, hop in enumerate(path):
            try:
                swaps.append({
                    'poolId': hop['pool_id'],
                    'assetInIndex': assets.index(hop['from_token']),
                    'assetOutIndex': assets.index(hop['to_token']),
                    'amount': value if i == 0 else 0,
                    'userData': b''
                })
                logger.debug(f"Added swap {i}: {hop['from_token']} -> {hop['to_token']}")
            except ValueError as e:
                logger.error(f"Error creating swap: {e}")
                return None

        # Set limits with 5% slippage
        slippage = 0.05
        limits = [int(value * (1 + slippage)) if i == 0 else 0 for i in range(len(assets))]

        # Finally append batch swap operation
        batch_calls.append({
            'client_name': 'balancerv2vault',
            'method': 'batchSwap',
            'params': {
                'kind': 0,  # GIVEN_IN
                'swaps': swaps,
                'assets': assets,
                'funds': {
                    'sender': sender,
                    'fromInternalBalance': False,
                    'recipient': sender,
                    'toInternalBalance': False
                },
                'limits': limits,
                'deadline': int(context.chain.blocks.head.timestamp + 3600)
            }
        })

        #circles_state = context.network_state['contract_states']['CirclesHub']['state']
        #token_balances = circles_state.get('token_balances')
        #print(token_balances[sender])

        # 4) Wrap CRC
        #_____________________________________
        client = context.get_client('circleshub')
        if not client:
            return {}

        id = client.toTokenId(sender) 
        balance = client.balanceOf(sender, id)
        wrap_amount = int(48e18)

        if balance < wrap_amount:
            return {}
        

         # Add approval for CirclesHub
        batch_calls.append({
            'client_name': 'circleshub',
            'method': 'setApprovalForAll',
            'params': {
                '_operator': CIRCLES_HUB,
                '_approved': True,
                'sender': sender,
                'value': 0
            }
        })

        # 5) Wrap CRC
        batch_calls.append({
            'client_name': 'circleshub',
            'method': 'wrap', 
            'params': {
                '_avatar': sender,
                '_amount': wrap_amount,
                '_type': 0,
                'sender': sender,
                'value': 0
            }
        })


        # 6) Create LBP Pool
        #_____________________________________
        
        client_circleserc20 = context.get_client('circleserc20lift')
        if not client_circleserc20:
            return {}
        CRC20 = client_circleserc20.erc20Circles(0,'0x42cEDde51198D1773590311E2A340DC06B24cB37')
        # Sort tokens and weights
        tokens = []
        weights = []
        weight1 = 10000000000000000  # 1%
        weight99 = 990000000000000000  # 99%

        # Ensure deterministic token order
        if CRC20 < BACKING_ASSET:
            tokens = [CRC20, BACKING_ASSET]
            weights = [weight1, weight99]
        else:
            tokens = [BACKING_ASSET, CRC20]
            weights = [weight99, weight1]

        batch_calls.append({
            'client_name': 'balancerv2lbpfactory',
            'method': 'create', 
            'params': {
                'name': 'Test Pool',
                'symbol': 'TP',
                'tokens': tokens,
                'weights': weights,
                'swapFeePercentage': 10000000000000000,  # 1%
                'owner': sender,
                'swapEnabledOnStart': True,
                'sender': sender,
                'value': 0
            }
        })

        # 7) Set WxDAI approval from VAULT
        #_____________________________________
        batch_calls.append({
            'client_name': 'erc20',
            'method': 'approve', 
            'params': {
                'token_address': BACKING_ASSET,
                'spender': VAULT,
                'amount': int(100e18), 
                'sender': sender,
                'value': 0
            }
        })
        batch_calls.append({
            'client_name': 'erc20',
            'method': 'approve', 
            'params': {
                'token_address': CRC20,
                'spender': VAULT,
                'amount': int(100e18), 
                'sender': sender,
                'value': 0
            }
        })

        params = {
            'sender': sender,
            'value': value,  # This value is used for the deposit operation
            'batch_calls': batch_calls
        }

        logger.debug(f"Built batch call sequence with {len(batch_calls)} operations")
        for i, call in enumerate(batch_calls):
            logger.debug(f"Operation {i}: {call['client_name']}.{call['method']}")
        
        return params

       

class DepositOnlyStrategy(BaseStrategy):
    """Strategy for simple xDAI deposit"""
    
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        value = int(1e18)  # 1 xDAI
            
        batch_calls = [
            {
                'client_name': 'wxdai',
                'method': 'deposit',
                'params': {}
            }
        ]
            
        return {
            'sender': sender,
            'value': value,
            'batch_calls': batch_calls
        }

# Map call names to strategy classes
available_calls = {
    'deposit': DepositOnlyStrategy,
    'deposit_and_swap': DepositAndSwapStrategy
}