from typing import Dict, List, Any
from ..registry import register_implementation, ContractCall
from ..base import BaseImplementation
from src.framework.core.context import SimulationContext
from src.framework.logging import get_logger
import logging
from ._utils import _get_pool_reserves, _find_arb_opportunity
import random

logger = get_logger(__name__, logging.INFO)


@register_implementation("custom_arbLBP")
class ArbLBP(BaseImplementation):

    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """Find and execute arbitrage across LBP pools"""
        sender = context.acting_address

        # Get all LBP pools
        try:
            LBPs_state = context.network_state['contract_states']['BalancerV2LBPFactory']['state']['LBPs']
            poolId_list = [poolId for poolId in LBPs_state.keys()]
            if not poolId_list:
                return []
        except:
            return []

        client_CRCDemurrageERC20 = context.get_client('circlesdemurrageerc20')
        if not client_CRCDemurrageERC20:
            return []

        # Collect pool data
        pools_data = []
        for poolId in poolId_list:
            tokens, balances = _get_pool_reserves(context, poolId)
            if not tokens or not balances:
                continue

            # Identify CRC token
            crc_token = None
            backing_token = None
            for token in tokens:
                try:
                    if client_CRCDemurrageERC20.avatar(token):
                        crc_token = token
                    else:
                        backing_token = token
                except:
                    continue

            if not (crc_token and backing_token):
                continue

            pools_data.append({
                'id': poolId,
                'crc_token': crc_token,
                'backing_token': backing_token,
                'balances': balances,
                'tokens': tokens,
                'avatar': client_CRCDemurrageERC20.avatar(crc_token),  # Store avatar for unwrapping
                'owner': LBPs_state[poolId]['owner'],
                'price': balances[1] / balances[0] if balances[0] > 0 else 0  # backing/crc ratio
            })


        if len(pools_data) < 2:
            return []

        # Find best arbitrage opportunity
        buy_pool_id, sell_pool_id, price_diff = _find_arb_opportunity(pools_data)
        if not buy_pool_id or price_diff < 0.02:  # 2% minimum difference
            return []

        # Get pool details
        buy_pool = next(p for p in pools_data if p['id'] == buy_pool_id)
        sell_pool = next(p for p in pools_data if p['id'] == sell_pool_id)

        # Build multi-step transaction
        batch_calls = []


        WXDAI = '0xe91d153e0b41518a2ce8dd3d7944fa863463a97d'
        VAULT = '0xBA12222222228d8Ba445958a75a0704d566BF2C8'

        crc_index = buy_pool['tokens'].index(buy_pool['crc_token'])
        backing_index = 1 - crc_index  # Since there are only 2 tokens

        # Use correct index for amount calculation
        amount_in = min(buy_pool['balances'][backing_index] // 100, 1000e18)

        # Calculate expected CRC amount from pool price
        pool_price = buy_pool['balances'][backing_index] / buy_pool['balances'][crc_index]
        slippage = 0.05  # 5% slippage
        amount_out = int((amount_in / pool_price) * (1 - slippage)) 

        print('===== ',amount_in)

        # 1. Deposit xDAI to get WXDAI
        batch_calls.append(
            ContractCall(
                client_name="wxdai",
                method="deposit",
                params={
                    "sender": sender,
                    "value": amount_in,
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
                    "amount": amount_in * 2,
                    "sender": sender,
                    "value": 0
                }
            )
        )

        # 3. Swap WXDAI to backing token if needed
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
                    'amount': amount_in if i == 0 else 0,
                    'userData': b''
                })

            slippage = 0.05
            limits = [int(amount_in * (1 + slippage)) if i == 0 else 0 for i in range(len(assets))]

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

        # 4. Approve backing token for vault
        batch_calls.append(
            ContractCall(
                client_name="erc20",
                method="approve",
                params={
                    "token_address": buy_pool['backing_token'],
                    "spender": VAULT,
                    "amount": amount_in * 2,
                    "sender": sender,
                    "value": 0
                }
            )
        )

        # 5. Buy CRC token from cheaper pool
        swap_deadline = context.chain.blocks.head.timestamp + 3600
        batch_calls.append(
            ContractCall(
                client_name="balancerv2vault",
                method="swap",
                params={
                    "sender": sender,
                    "value": 0,
                    "singleSwap": {
                        "poolId": buy_pool_id,
                        "kind": 1,  # GIVEN_OUT 
                        "assetIn": buy_pool['backing_token'],
                        "assetOut": buy_pool['crc_token'],
                        "amount": amount_out,
                        "userData": b''
                    },
                    "funds": {
                        "sender": sender,
                        "fromInternalBalance": False,
                        "recipient": sender,
                        "toInternalBalance": False
                    },
                    "limit": amount_in,
                    "deadline": swap_deadline
                }
            )
        )


        batch_calls.append(
            ContractCall(
                client_name="circlesdemurrageerc20",
                method="unwrap",
                params={
                    "sender": sender,
                    "value": 0,
                    "contract_address": buy_pool['crc_token'],
                    "_amount": amount_out,
                },
            )
        )


        client_Hub = context.get_client('circleshub')
        if not client_Hub:
            return []

        # TODO: Add unwrap, pathfinding arbitrage, wrap steps
        # These would follow similar pattern to your existing PathFinderArb
        
        # Step N: Swap in sell pool
        batch_calls2 = []
        batch_calls2.append(
            ContractCall(
                client_name="balancerv2vault",
                method="swap",
                params={
                    "sender": sender,
                    "value": 0,
                    "singleSwap": {
                        "poolId": sell_pool_id,
                        "kind": 0,  # GIVEN_IN
                        "assetIn": sell_pool['crc_token'],
                        "assetOut": sell_pool['backing_token'],
                        "amount": amount_in,  # Use same amount for example
                        "userData": b''
                    },
                    "funds": {
                        "sender": sender,
                        "fromInternalBalance": False,
                        "recipient": sender,
                        "toInternalBalance": False
                    },
                    "limit": 0,
                    "deadline": swap_deadline
                }
            )
        )

        return batch_calls