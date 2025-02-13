from typing import Dict, List, Any
from ...registry import register_implementation, ContractCall
from ...base import BaseImplementation
from src.framework.core.context import SimulationContext
from src.framework.logging import get_logger
import logging

logger = get_logger(__name__, logging.INFO)

@register_implementation("custom_arbSellToLBP")
class ArbSellToLBP(BaseImplementation):
    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Sell wrapped CRC to more expensive pool in chunks"""
        sender = context.acting_address

        # Get stored arbitrage info
        arb_info = context.get_running_state('arb_check')
        if not arb_info:
            return []

        # Get sell pool data and expected amount
        sell_pool = arb_info.get('sell_pool_data')
        if not sell_pool:
            return []

        # Get the amount we wrapped from arbitrage
        wrapped_amount = arb_info.get('wrapped_amount')
        if not wrapped_amount:
            logger.warning("No wrapped amount found in arb_info")
            return []

        # Check actual wrapped token balance
        erc20_client = context.get_client('erc20')
        if not erc20_client:
            return []

        current_balance = erc20_client.balance_of(sell_pool['crc_token'], sender)
        if current_balance == 0:
            return []

        # Only sell the amount that came from our arbitrage
        sell_amount = min(current_balance, wrapped_amount)
        logger.info(f"Selling {sell_amount} tokens out of {current_balance} total balance")

        VAULT = '0xBA12222222228d8Ba445958a75a0704d566BF2C8'
        batch_calls = []

        # Get current pool reserves - properly handle 3 return values
        vault_client = context.get_client('balancerv2vault')
        tokens, balances, _ = vault_client.getPoolTokens(sell_pool['id'])
        if not tokens or not balances:
            return []

        # Find CRC token index in pool
        try:
            crc_index = tokens.index(sell_pool['crc_token'])
            pool_crc_balance = balances[crc_index]
        except (ValueError, IndexError):
            logger.error("Failed to find CRC token in pool tokens")
            return []

        # Calculate maximum amount per swap (20% of pool reserves)
        #max_per_swap = int(pool_crc_balance * 0.2)
        
        max_per_swap = int(sell_amount * 0.2)
        
        # Split sell amount into chunks
        remaining_amount = sell_amount
        total_chunks = []
        
        while remaining_amount > 0:
            chunk = min(remaining_amount, max_per_swap)
            if chunk == 0:
                break
            total_chunks.append(chunk)
            remaining_amount -= chunk

        if not total_chunks:
            return []

        # 1. Approve wrapped token for vault
        batch_calls.append(
            ContractCall(
                client_name="erc20",
                method="approve",
                params={
                    "token_address": sell_pool['crc_token'],
                    "spender": VAULT,
                    "amount": sell_amount * 2,  # Extra allowance for safety
                    "sender": sender,
                    "value": 0
                }
            )
        )

        # 2. Create multiple swaps for each chunk
        swap_deadline = context.chain.blocks.head.timestamp + 3600
        
        for chunk_amount in total_chunks:
            batch_calls.append(
                ContractCall(
                    client_name="balancerv2vault",
                    method="swap",
                    params={
                        "sender": sender,
                        "value": 0,
                        "singleSwap": {
                            "poolId": sell_pool['id'],
                            "kind": 0,  # GIVEN_IN
                            "assetIn": sell_pool['crc_token'],
                            "assetOut": sell_pool['backing_token'],
                            "amount": chunk_amount,
                            "userData": b''
                        },
                        "funds": {
                            "sender": sender,
                            "fromInternalBalance": False,
                            "recipient": sender,
                            "toInternalBalance": False
                        },
                        "limit": 0,  # No limit when selling
                        "deadline": swap_deadline
                    }
                )
            )

        return batch_calls