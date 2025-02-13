from typing import Dict, List, Any
from ...registry import register_implementation, ContractCall
from ...base import BaseImplementation
from src.framework.core.context import SimulationContext
from src.framework.logging import get_logger
import logging

logger = get_logger(__name__, logging.INFO)

@register_implementation("custom_arbWrapCRC")
class ArbWrapCRC(BaseImplementation):
    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Wrap CRC tokens for final sale"""
        sender = context.acting_address

        # Get stored arbitrage info
        arb_info = context.get_running_state('arb_check')
        if not arb_info:
            return []

        # Get sell pool data
        sell_pool = arb_info.get('sell_pool_data')
        if not sell_pool:
            return []

        # Get the received_crc_amount from previous steps
        received_amount = arb_info.get('received_crc_amount')
        if not received_amount:
            logger.warning("No received CRC amount found in arb_info")
            return []

        # Check CirclesHub state for actual unwrapped balance
        hub_state = context.network_state['contract_states']['CirclesHub']['state']
        token_balances = hub_state.get('token_balances', {})
        sender_balances = token_balances.get(sender, {})

        # Find balance of sell pool's unwrapped token
        unwrapped_balance = 0
        unwrapped_crc = sell_pool['unwrapped_crc']
        
        # Need to convert avatar address to token ID for balance lookup
        client = context.get_client('circleshub')
        if not client:
            return []
            
        token_id = client.toTokenId(unwrapped_crc)
        
        # Check balance in token_balances
        for id, balance_info in sender_balances.items():
            if str(id) == str(token_id):
                unwrapped_balance = balance_info['balance']
                break

        if unwrapped_balance == 0:
            return []

        # Only wrap the amount we received from arbitrage path
        wrap_amount = min(unwrapped_balance, received_amount)
        logger.info(f"Wrapping {wrap_amount} tokens out of {unwrapped_balance} total balance")

        # Store wrap amount for sell step
        arb_info['wrapped_amount'] = wrap_amount
        context.update_running_state({'arb_check': arb_info})

        return [
            ContractCall(
                client_name="circleshub",
                method="wrap",
                params={
                    "sender": sender,
                    "value": 0,
                    "_avatar": unwrapped_crc,
                    "_amount": wrap_amount,
                    "_type": 0,
                }
            )
        ]