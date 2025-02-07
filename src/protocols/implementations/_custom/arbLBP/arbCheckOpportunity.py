from typing import Dict, List, Any
from ...registry import register_implementation, ContractCall
from ...base import BaseImplementation
from src.framework.core.context import SimulationContext
from src.framework.logging import get_logger
import logging
from .._utils import _analyze_arbitrage, _find_arb_opportunity
from datetime import datetime
import copy

logger = get_logger(__name__, logging.INFO)

@register_implementation("custom_arbCheckOpportunity")
class ArbCheckOpportunity(BaseImplementation):
    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """
        Check for arbitrage opportunities by:
        1. Finding potential pool pairs
        2. Testing pathfinder flow with simulated balances
        3. Comparing potential profit
        Returns empty list but always succeeds
        """
        try:
            sender = context.acting_address

            # Get all LBP pools
            LBPs_state = context.network_state['contract_states']['BalancerV2LBPFactory']['state']['LBPs']
            if not LBPs_state:
                return []  # Still counts as success

            client_CRCDemurrage = context.get_client('circlesdemurrageerc20')
            if not client_CRCDemurrage:
                return []  # Still counts as success

            # Store original CirclesHub state to restore later
            original_hub_state = copy.deepcopy(context.network_state['contract_states']['CirclesHub']['state'])

            # Collect pool data and identify opportunities
            pools_data = []
            for poolId, pool_info in LBPs_state.items():
                try:
                    tokens = pool_info['tokens']
                    tokens_balances = context.get_client('balancerv2vault').getPoolTokens(poolId)[1]

                    # Identify CRC and backing tokens
                    crc_token = None 
                    unwrapped_crc = None
                    backing_token = None
                    for token in tokens:
                        try:
                            avatar_addr = client_CRCDemurrage.avatar(token)
                            if avatar_addr:
                                crc_token = token
                                unwrapped_crc = avatar_addr
                            else:
                                backing_token = token
                        except:
                            continue

                    if not (crc_token and backing_token):
                        continue

                    pools_data.append({
                        'id': poolId,
                        'crc_token': crc_token,
                        'unwrapped_crc': unwrapped_crc,
                        'backing_token': backing_token,
                        'balances': tokens_balances,
                        'tokens': tokens,
                        'price': tokens_balances[1] / tokens_balances[0] if tokens_balances[0] > 0 else 0
                    })
                except Exception as e:
                    logger.error(f"Error processing pool {poolId}: {e}")
                    continue  # Skip problematic pools but continue checking others

            if len(pools_data) < 2:
                return []  # Still counts as success

            # Find potential arbitrage pairs
            buy_pool_id, sell_pool_id, price_diff = _find_arb_opportunity(pools_data)
            if not buy_pool_id or price_diff < 0.02:  # 2% minimum difference
                return []  # Still counts as success

            # Get pool details
            buy_pool = next(p for p in pools_data if p['id'] == buy_pool_id)
            sell_pool = next(p for p in pools_data if p['id'] == sell_pool_id)

            test_amount = 79e30

            # Temporarily modify CirclesHub state to simulate having unwrapped tokens
            hub_state = context.network_state['contract_states']['CirclesHub']['state']
            
            # Store token balances state before modification
            if 'token_balances' not in hub_state:
                hub_state['token_balances'] = {}
            original_balances = hub_state['token_balances'].copy()
            
            # Add simulated balance for testing
            test_balance = {
                'balance': test_amount,
                'last_day_updated': datetime.fromtimestamp(context.chain.blocks.head.timestamp).date()
            }

            if sender not in hub_state['token_balances']:
                hub_state['token_balances'][sender] = {}
                
            # Add simulated balance for buy token
            hub_state['token_balances'][sender][buy_pool['unwrapped_crc']] = test_balance

            # Rebuild graph with simulated balances
            context.rebuild_graph()

            # Test potential flow
            max_flow, _, edge_flows, _ = _analyze_arbitrage(
                context,
                sender,
                buy_pool['unwrapped_crc'],  # START_TOKEN: unwrapped version of buy token
                sell_pool['unwrapped_crc']  # END_TOKEN: unwrapped version of sell token
            )

            # Restore original state
            context.network_state['contract_states']['CirclesHub']['state'] = original_hub_state

            # If we found viable arbitrage, store info for sequence
            if max_flow > 0:
                logger.info(f"Found arbitrage opportunity conversion Amount: {max_flow / 1e3}")
                
                # Store arbitrage info for sequence
                context.update_running_state({
                    'arb_check': {
                        'buy_pool_id': buy_pool_id,
                        'sell_pool_id': sell_pool_id,
                        'buy_pool_data': buy_pool,
                        'sell_pool_data': sell_pool,
                        'max_flow': max_flow,
                        'edge_flows': edge_flows,
                        'buy_unwrapped': buy_pool['unwrapped_crc'],
                        'sell_unwrapped': sell_pool['unwrapped_crc']
                    }
                })

                return [
                    ContractCall(
                        client_name="master",
                        method="noop",  # This method will do nothing
                        params={"sender": context.acting_address}
                    )
                ]

        except Exception as e:
            logger.error(f"Error in arbitrage check: {e}")
            # Even if we hit an error, still count as success
        
            return [
                    ContractCall(
                        client_name="master",
                        method="noop",
                        params={"sender": context.acting_address}
                    )
                ]