from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext
from src.framework.logging import get_logger
import logging
import random

logger = get_logger(__name__, logging.INFO)

@register_implementation("custom_setupLBP")
class SetupLBP(BaseImplementation):

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:

        sender = context.acting_address

        client = context.get_client("circleshub")
        if not client:
            return []
        
        client_circleserc20 = context.get_client('circleserc20lift')
        if not client_circleserc20:
            return {}
        
        VAULT = '0xBA12222222228d8Ba445958a75a0704d566BF2C8'
        WXDAI = '0xe91d153e0b41518a2ce8dd3d7944fa863463a97d'
        CIRCLES_HUB = '0xc12C1E50ABB450d6205Ea2C3Fa861b3B834d13e8' 

        # Get constraints from profile
        constraints = context.agent.profile.get_action_config("custom_setupLBP").constraints
        XDAI_AMOUNT = int(constraints.get('XDAI_AMOUNT',100) * 1e18 )
        CRC_AMOUNT = int(constraints.get('CRC_AMOUNT',48) * 1e18 )
        CRC_TOKEN = constraints.get('CRC_TOKEN',sender)
        WRAP_TYPE = constraints.get('WRAP_TYPE',0)
        BACKING_ASSET = constraints.get('BACKING_ASSET','0xaf204776c7245bF4147c2612BF6e5972Ee483701')
        WEIGHT_CRC = constraints.get('WEIGHT_CRC',10000000000000000)
        WEIGHT_BACKING = constraints.get('WEIGHT_BACKING',990000000000000000)

        batch_calls = []


        # 1) xDAI deposit operation
        #_____________________________________
        batch_calls.append(
            ContractCall(
                client_name="wxdai",
                method="deposit",
                params={
                    "sender": sender,
                    "value": XDAI_AMOUNT,
                }
            )
        )

        # 2) Set WxDAI approval from VAULT
        #_____________________________________
        batch_calls.append(
            ContractCall(
                client_name="erc20",
                method="approve",
                params={
                    "token_address": WXDAI,
                    "spender": VAULT,
                    "amount": XDAI_AMOUNT * 2, 
                    "sender": sender,
                    "value": 0
                }
            )
        )

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
                    'amount': XDAI_AMOUNT if i == 0 else 0,
                    'userData': b''
                })
                logger.debug(f"Added swap {i}: {hop['from_token']} -> {hop['to_token']}")
            except ValueError as e:
                logger.error(f"Error creating swap: {e}")
                return None

        # Set limits with 5% slippage
        slippage = 0.05
        limits = [int(XDAI_AMOUNT * (1 + slippage)) if i == 0 else 0 for i in range(len(assets))]

        # Finally append batch swap operation
        batch_calls.append(
            ContractCall(
                client_name="balancerv2vault",
                method="batchSwap",
                params={
                    "kind": 0,  # GIVEN_IN
                    "swaps": swaps,
                    "assets": assets,
                    "funds": {
                        "sender": sender,
                        "fromInternalBalance": False,
                        "recipient": sender,
                        "toInternalBalance": False
                    },
                    "limits": limits,
                    "deadline": int(context.chain.blocks.head.timestamp + 3600),
                    "sender": sender,
                    "value": 0
                }
            )
        )


        # 4) Set Approval on Hub
        #_____________________________________
        batch_calls.append(
            ContractCall(
                client_name="circleshub",
                method="setApprovalForAll",
                params={
                    '_operator': CIRCLES_HUB,
                    '_approved': True,
                    'sender': sender,
                    'value': 0
                }
            )
        )

        # 5) Wrap CRC
        #_____________________________________
        id = client.toTokenId(CRC_TOKEN) 
        balance = client.balanceOf(sender, id)
        
        if balance < CRC_AMOUNT:
            logger.debug(f"Balance {balance} < {CRC_AMOUNT}")
            return {}
        
        batch_calls.append(
            ContractCall(
                client_name="circleshub",
                method="wrap",
                params={
                    '_avatar': CRC_TOKEN,
                    '_amount': CRC_AMOUNT,
                    '_type': WRAP_TYPE,
                    'sender': sender,
                    'value': 0
                }
            )
        )

        # 6) Create LBP Pool
        #_____________________________________

        CRC20 = client_circleserc20.erc20Circles(WRAP_TYPE,CRC_TOKEN)
        # Sort tokens and weights, Ensure deterministic token order
        tokens = [CRC20, BACKING_ASSET]
        weights = [WEIGHT_CRC, WEIGHT_BACKING]

        if tokens[0].lower() > tokens[1].lower():
            tokens = tokens[::-1]
            weights = weights[::-1]

        id = str(random.randint(0,1000000))

        batch_calls.append(
            ContractCall(
                client_name="balancerv2lbpfactory",
                method="create",
                params={
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
            )
        )

        # 7) Set WxDAI/CRC approval from VAULT
        #_____________________________________
        batch_calls.append(
            ContractCall(
                client_name="erc20",
                method="approve",
                params={
                    'token_address': BACKING_ASSET,
                    'spender': VAULT,
                    'amount': int(100e18), 
                    'sender': sender,
                    'value': 0
                }
            )
        )

        batch_calls.append(
            ContractCall(
                client_name="erc20",
                method="approve",
                params={
                    'token_address': CRC20,
                    'spender': VAULT,
                    'amount': int(100e18), 
                    'sender': sender,
                    'value': 0
                }
            )
        )

        return batch_calls
