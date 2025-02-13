from typing import Dict, List, Any
from ...registry import register_implementation, ContractCall
from ...base import BaseImplementation
from src.framework.core.context import SimulationContext
from src.framework.logging import get_logger
import logging

logger = get_logger(__name__, logging.INFO)

@register_implementation("custom_arbUnWrapCRC")
class ArbUnWrapCRC(BaseImplementation):
    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Unwrap CRC tokens obtained from buy"""
        sender = context.acting_address

        # Get stored arbitrage info
        arb_info = context.get_running_state('arb_check')
        if not arb_info:
            return []

        # Get current pool data
        buy_pool = arb_info.get('buy_pool_data')
        if not buy_pool:
            return []
        
        sell_pool = arb_info.get('sell_pool_data')
        if not sell_pool:
            return []

        # Get actual CRC balance
        erc20_client = context.get_client('erc20')
        if not erc20_client:
            return []

        crc_balance = erc20_client.balance_of(buy_pool['crc_token'], sender)
        if crc_balance == 0:
            return []

        # Store unwrap amount in state for path finding
        arb_info['received_crc_amount'] = 10**18 #crc_balance
        context.update_running_state({'arb_check': arb_info})

        # Add address to be checked for balance updates
        if 'additional_balance_checks' not in context.network_state:
            context.network_state['additional_balance_checks'] = []
        if arb_info.get('buy_unwrapped'):
            if arb_info.get('buy_unwrapped') not in context.network_state['additional_balance_checks']:
                context.network_state['additional_balance_checks'].append(arb_info.get('buy_unwrapped'))
            if arb_info.get('sell_unwrapped') not in context.network_state['additional_balance_checks']:
                context.network_state['additional_balance_checks'].append(arb_info.get('sell_unwrapped'))


        print(context.network_state['additional_balance_checks'])
        batch_calls = []

        batch_calls.append(
            ContractCall(
                client_name="circlesdemurrageerc20",
                method="unwrap",
                params={
                    "sender": sender,
                    "value": 0,
                    "contract_address": buy_pool['crc_token'],
                    "_amount": crc_balance,
                }
            ))
        
        if arb_info['needs_trust']:
            print({
                        "sender": sender,
                        "value": 0,
                        "_trustReceiver": sell_pool['unwrapped_crc'],
                        "_expiry": context.chain.blocks.head.timestamp + 10*24*60*60  # 1 day expiry,
                    })
            block_timestamp = context.chain.blocks.head.timestamp
            expiry_delta = 10 * 24 * 60 * 60
            expiry = int(block_timestamp + expiry_delta)

            batch_calls.append(
                ContractCall(
                    client_name="circleshub",
                    method="trust",
                    params={
                        "sender": sender,
                        "value": 0,
                        "_trustReceiver": sell_pool['unwrapped_crc'],
                        "_expiry": expiry  # 1 day expiry,
                    },
                )
            )
        
        return batch_calls