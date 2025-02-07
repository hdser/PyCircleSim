from typing import Dict, List, Any
from ...registry import register_implementation, ContractCall
from ...base import BaseImplementation
from src.framework.core.context import SimulationContext
from src.framework.logging import get_logger
import logging

logger = get_logger(__name__, logging.INFO)

@register_implementation("custom_arbBuyCRC")
class ArbBuyCRC(BaseImplementation):
    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Buy CRC tokens from cheaper pool"""
        sender = context.acting_address

        # Get stored arbitrage info
        arb_info = context.get_running_state('arb_check')
        if not arb_info:
            return []

        buy_pool = arb_info['buy_pool_data']
        expected_amount = arb_info.get('expected_backing_amount', 0)
        VAULT = '0xBA12222222228d8Ba445958a75a0704d566BF2C8'

        # Get current backing token balance to know how much we got
        erc20_client = context.get_client('erc20')
        if not erc20_client:
            return []

        backing_balance = erc20_client.balance_of(
            buy_pool['backing_token'], 
            sender
        )

        if backing_balance < expected_amount:
            logger.warning(f"Actual balance {backing_balance} less than expected {expected_amount}")
            return []

        batch_calls = []
        # 1. Approve backing token for vault
        batch_calls.append(
            ContractCall(
                client_name="erc20",
                method="approve",
                params={
                    "token_address": buy_pool['backing_token'],
                    "spender": VAULT,
                    "amount": expected_amount * 2,  # Extra allowance for safety
                    "sender": sender,
                    "value": 0
                }
            )
        )


        # 2. Buy CRC token from cheaper pool
        swap_deadline = context.chain.blocks.head.timestamp + 3600
        batch_calls.append(
            ContractCall(
                client_name="balancerv2vault",
                method="swap",
                params={
                    "sender": sender,
                    "value": 0,
                    "singleSwap": {
                        "poolId": buy_pool['id'],
                        "kind": 0,  # GIVEN_IN
                        "assetIn": buy_pool['backing_token'],
                        "assetOut": buy_pool['crc_token'],
                        "amount": expected_amount,
                        "userData": b''
                    },
                    "funds": {
                        "sender": sender,
                        "fromInternalBalance": False,
                        "recipient": sender,
                        "toInternalBalance": False
                    },
                    "limit": 0,  # No limit when buying
                    "deadline": swap_deadline
                }
            )
        )

        # Store current pool data for later steps
        arb_info['current_pool'] = buy_pool
        arb_info['backing_amount_used'] = expected_amount
        context.update_running_state({'arb_check': arb_info})

        return batch_calls