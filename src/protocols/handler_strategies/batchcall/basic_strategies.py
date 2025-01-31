from typing import Dict, Any, Optional
from src.protocols.handler_strategies.base import BaseStrategy
from src.framework.core import SimulationContext
from src.framework.logging import get_logger
import random
import logging

logger = get_logger(__name__,logging.DEBUG)

def get_constraints(sequence_name, sequence_step, context):
    constraints = {}
    for sequence in context.agent.profile.sequences:
        if sequence.name==sequence_name:
            for step in sequence.steps:
                if step.batchcall:
                    if sequence_step in step.batchcall.keys():
                        constraints = step.constraints
    return constraints
        

class SetupLBPStrategy(BaseStrategy):
    """Strategy for depositing xDAI and swapping on Balancer"""
    
    def get_params(self, context: SimulationContext) -> Optional[Dict[str, Any]]:
        sender = self.get_sender(context)
        if not sender:
            return None
            
        
        VAULT = '0xBA12222222228d8Ba445958a75a0704d566BF2C8'
        WXDAI = '0xe91d153e0b41518a2ce8dd3d7944fa863463a97d'
        CIRCLES_HUB = '0xc12C1E50ABB450d6205Ea2C3Fa861b3B834d13e8' 

        constraints = get_constraints('full_setup_lbp','setup_lbp', context)
        #constraints = self.get_constraints(context,'full_setup_lbp', 'setup_lbp')
        xDAI_value = int(constraints.get('xDAI_value',100) * 1e18 )
        CRC_value = int(constraints.get('CRC_value',48) * 1e18 )
        CRC_token = constraints.get('CRC_token',sender)
        WRAP_TYPE = constraints.get('WRAP_TYPE',0)
        BACKING_ASSET = constraints.get('BACKING_ASSET','0xaf204776c7245bF4147c2612BF6e5972Ee483701')
        

        batch_calls = []

        # 1) xDAI deposit operation
        #_____________________________________
        batch_calls.append({
            'client_name': 'wxdai',
            'method': 'deposit',
            'params': {
                'sender': sender,
                'value': xDAI_value
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
                'amount': xDAI_value * 2, 
                'sender': sender,
                'value': 0
            }
        })

        path_price = context.find_swap_path(BACKING_ASSET, '0x2a22f9c3b484c3629090FeED35F17Ff8F88f76F0')
        print(path_price)
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
                    'amount': xDAI_value if i == 0 else 0,
                    'userData': b''
                })
                logger.debug(f"Added swap {i}: {hop['from_token']} -> {hop['to_token']}")
            except ValueError as e:
                logger.error(f"Error creating swap: {e}")
                return None

        # Set limits with 5% slippage
        slippage = 0.05
        limits = [int(xDAI_value * (1 + slippage)) if i == 0 else 0 for i in range(len(assets))]

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
                'deadline': int(context.chain.blocks.head.timestamp + 3600),
                'sender': sender,
                'value': 0
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

        id = client.toTokenId(CRC_token) 
        balance = client.balanceOf(sender, id)
        print(sender, CRC_token, id, balance)
        
        
        if balance < CRC_value:
            logger.debug(f"Balance {balance} < {CRC_value}")
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
                '_avatar': CRC_token,
                '_amount': CRC_value,
                '_type': WRAP_TYPE,
                'sender': sender,
                'value': 0
            }
        })


        # 6) Create LBP Pool
        #_____________________________________

        client_circleserc20 = context.get_client('circleserc20lift')
        if not client_circleserc20:
            return {}
        CRC20 = client_circleserc20.erc20Circles(0,CRC_token)
        print(CRC_token, CRC20)
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

        id = str(random.randint(0,1000000))
        batch_calls.append({
            'client_name': 'balancerv2lbpfactory',
            'method': 'create', 
            'params': {
                'name': 'crc-test'+ id,
                'symbol': 'TP'+ id,
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
            'value': xDAI_value,  # This value is used for the deposit operation
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
    'setup_lbp': SetupLBPStrategy
}