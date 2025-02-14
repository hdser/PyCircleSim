from typing import Dict, List, Any
from ...registry import register_implementation, ContractCall
from ...base import BaseImplementation
from src.framework.core.context import SimulationContext
from src.framework.logging import get_logger
import logging

logger = get_logger(__name__, logging.INFO)

@register_implementation("custom_arbGetBackingToken")
class ArbGetBackingToken(BaseImplementation):
    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Get initial backing token and convert if needed"""
        sender = context.acting_address

        # Get stored arbitrage info
        arb_info = context.get_running_state('arb_check')
        if not arb_info:
            return []

        WXDAI = '0xe91d153e0b41518a2ce8dd3d7944fa863463a97d'
        VAULT = '0xBA12222222228d8Ba445958a75a0704d566BF2C8'
        buy_pool = arb_info['buy_pool_data']
        
        # Use optimal amount to determine WXDAI needed
        optimal_amount = arb_info.get('optimal_amount', 10**18)  # Default to 10 if not set
        xdai_amount = int(optimal_amount * 1.1)  # Add 10% buffer for slippage

        batch_calls = []
        # 1. Deposit xDAI to get WXDAI
        batch_calls.append(
            ContractCall(
                client_name="wxdai",
                method="deposit",
                params={
                    "sender": sender,
                    "value": xdai_amount,
                }
            )
        )

        # 2. Approve WXDAI for Vault
        batch_calls.append(
            ContractCall(
                client_name="erc20",
                method="approve",
                params={
                    "token_address": WXDAI,
                    "spender": VAULT,
                    "amount": xdai_amount * 2,  # Double for safety
                    "sender": sender,
                    "value": 0
                }
            )
        )

        # 3. If needed, swap WXDAI to backing token
        if buy_pool['backing_token'].lower() != WXDAI.lower():
            path = context.find_swap_path(WXDAI, buy_pool['backing_token'])
            if not path:
                logger.warning(f"No path found between WXDAI and {buy_pool['backing_token']}")
                return []

            assets = [WXDAI.lower()]
            for hop in path:
                if hop['to_token'] not in assets:
                    assets.append(hop['to_token'])

            swaps = []
            for i, hop in enumerate(path):
                swaps.append({
                    'poolId': hop['pool_id'],
                    'assetInIndex': assets.index(hop['from_token']),
                    'assetOutIndex': assets.index(hop['to_token']),
                    'amount': xdai_amount if i == 0 else 0,
                    'userData': b''
                })

            # Store expected backing amount in state
            expected_backing = int(optimal_amount * 0.95)  # Account for 5% slippage
            arb_info['expected_backing_amount'] = expected_backing
            context.update_running_state({'arb_check': arb_info})

            slippage = 0.05
            limits = [int(xdai_amount * (1 + slippage)) if i == 0 else 0 for i in range(len(assets))]

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

        return batch_calls