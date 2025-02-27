
from typing import Dict, List, Any
from ...registry import register_implementation, ContractCall
from ...base import BaseImplementation
from src.framework.core.context import SimulationContext
from src.framework.logging import get_logger
import logging
from .._utils import _analyze_arbitrage, _find_arb_opportunity, _calculate_optimal_swap_amount
from datetime import datetime
import copy

logger = get_logger(__name__, logging.INFO)

@register_implementation("custom_arbCheckOpportunity")
class ArbCheckOpportunity(BaseImplementation):
    def get_calls(self, context: SimulationContext) -> List[ContractCall]:
        """
        1) Gather all LBP pools from 'BalancerV2LBPFactory' state.
        2) Identify which token is CRC vs. backing (compute price = backing_balance / crc_balance).
        3) Use `_find_arb_opportunity` to see if there's a sufficient difference and large feasible swap.
        4) If found, do a test flow with artificially added balance & trust to see if path is feasible.
        5) Save that info into `context` for next steps in the sequence.
        6) Always restore any state modifications before returning.

        Returns empty (a 'noop') if no opportunity or after storing info in `context`.
        """
        original_hub_state = copy.deepcopy(context.network_state['contract_states']['CirclesHub']['state'])
        try:
            sender = context.acting_address

            # 1. Collect LBP pools
            factory_state = context.network_state['contract_states'].get('BalancerV2LBPFactory', {})
            if not factory_state or 'LBPs' not in factory_state.get('state', {}):
                logger.info("No LBP pools in state.")
                return []

            LBPs_state = factory_state['state']['LBPs']
            if not LBPs_state:
                logger.info("LBP list is empty.")
                return []

            client_demurrage = context.get_client("circlesdemurrageerc20")
            if not client_demurrage:
                logger.warning("No circlesdemurrageerc20 client found.")
                return []

            balancer_vault = context.get_client("balancerv2vault")
            if not balancer_vault:
                logger.warning("No balancerv2vault client found.")
                return []
            
            balancer_lbp = context.get_client("balancerv2lbp")
            if not balancer_lbp:
                logger.warning("No balancerv2lbp client found.")
                return []
            

            # 2. Build up a list of pool dicts
            pools_data = []
            for poolId, pool_info in LBPs_state.items():
                try:
                    tokens = pool_info['tokens']
                    balances = balancer_vault.getPoolTokens(poolId)[1] 
                    poolAddress = pool_info['poolAddress']
                    weights = balancer_lbp.getNormalizedWeights(poolAddress)

                    # Identify CRC vs. backing
                    crc_token = None
                    unwrapped_crc = None
                    backing_token = None

                    for t in tokens:
                        try:
                            avatar_addr = client_demurrage.avatar(t)
                            if avatar_addr:
                                crc_token = t
                                unwrapped_crc = avatar_addr
                            else:
                                backing_token = t
                        except:
                            # If call fails => treat as backing
                            backing_token = t

                    if not (crc_token and backing_token):
                        continue

                    crc_idx = tokens.index(crc_token)
                    backing_idx = tokens.index(backing_token)

                    crc_balance = balances[crc_idx]/float(weights[crc_idx])
                    backing_balance = balances[backing_idx]/float(weights[backing_idx])

                    # Avoid division by zero or negative
                    if crc_balance <= 0:
                        continue

                    price = backing_balance / float(crc_balance)

                    pools_data.append({
                        'id': poolId,
                        'crc_token': crc_token,
                        'unwrapped_crc': unwrapped_crc,
                        'backing_token': backing_token,
                        'balances': balances,
                        'tokens': tokens,
                        'token_indices': {
                            'crc': crc_idx,
                            'backing': backing_idx
                        },
                        'price': price
                    })

                except Exception as e:
                    logger.error(f"Error processing pool {poolId}: {e}")
                    continue

            if len(pools_data) < 2:
                logger.info("Fewer than 2 LBP pools, cannot arbitrage.")
                return []

            # 3. Find potential arbitrage (the updated version returns feasible_amount as well)
            buy_pool_id, sell_pool_id, price_diff, feasible_amount = _find_arb_opportunity(
                pools_data,
                min_diff_threshold=0.02,      # e.g. require 2% price gap
                min_swap_threshold=10**17     # e.g. must be at least 0.1 CRC if decimals=18
            )

            if not buy_pool_id or price_diff < 0.02:
                logger.info(f"No arbitrage found above threshold. Best diff was {price_diff}.")
                return []
            if feasible_amount <= 10**17:
                logger.info(f"Feasible swap amount was too low: {feasible_amount}. Skipping.")
                return []

            # Identify the chosen buy/sell pools from the data
            buy_pool = next(p for p in pools_data if p['id'] == buy_pool_id)
            sell_pool = next(p for p in pools_data if p['id'] == sell_pool_id)

            # For clarity, we already know the feasible_amount from the function,
            # but let's log it again:
            logger.info(f"Selected buy_pool={buy_pool_id}, sell_pool={sell_pool_id}, diff={price_diff}, feasible={feasible_amount}")

            # 4. (Optional) Double-check or do additional logic:
            #    In your code, you recalc buy_amount & sell_amount just for logging:
            buy_amount = _calculate_optimal_swap_amount(
                buy_pool['tokens'],
                buy_pool['balances'],
                buy_pool['token_indices']['backing'],  # supply backing
                buy_pool['token_indices']['crc']       # receive CRC
            )
            sell_amount = _calculate_optimal_swap_amount(
                sell_pool['tokens'],
                sell_pool['balances'],
                sell_pool['token_indices']['crc'],     # supply CRC
                sell_pool['token_indices']['backing']  # receive backing
            )
            actual_amount = min(buy_amount, sell_amount)
            logger.info(f"Potential buy_amount={buy_amount}, sell_amount={sell_amount}, using={actual_amount} from pools.")

            # If we want to confirm it matches feasible_amount:
            if actual_amount != feasible_amount:
                logger.warning("Warning: feasible_amount differs from final recalculation. Possibly pool states changed in the interim.")

            # 5. Insert large test balance, trust, etc., then do a path check
            test_amount = 9e30
            hub_state = context.network_state['contract_states']['CirclesHub']['state']
            if 'token_balances' not in hub_state:
                hub_state['token_balances'] = {}
            if sender not in hub_state['token_balances']:
                hub_state['token_balances'][sender] = {}

            hub_state['token_balances'][sender][buy_pool['unwrapped_crc']] = {
                'balance': test_amount,
                'last_day_updated': datetime.fromtimestamp(context.chain.blocks.head.timestamp).date()
            }

            # Insert trust if needed
            if 'trustMarkers' not in hub_state:
                hub_state['trustMarkers'] = {}
            if sender not in hub_state['trustMarkers']:
                hub_state['trustMarkers'][sender] = {}

            circles_hub_client = context.get_client('circleshub')
            need_trust = False
            if not circles_hub_client.isTrusted(sender, sell_pool['unwrapped_crc']):
                need_trust = True
                # set an expiry well in the future
                hub_state['trustMarkers'][sender][sell_pool['unwrapped_crc']] = (
                    context.chain.blocks.head.timestamp + 365*24*60*60
                )

            context.rebuild_graph()

            # Check if we can now flow from buy_unwrapped -> sell_unwrapped
            max_flow, _, edge_flows, _ = _analyze_arbitrage(
                context,
                sender,
                buy_pool['unwrapped_crc'],
                sell_pool['unwrapped_crc'],
                cutoff=None
            )

            # Restore old state
            context.network_state['contract_states']['CirclesHub']['state'] = original_hub_state
            context.rebuild_graph()

            if max_flow > 0:
                logger.info(f"Found feasible path with flow={max_flow}. Price diff={price_diff}, feasible_amount={feasible_amount}")

                # Save details for next steps
                context.update_running_state({
                    'arb_check': {
                        'buy_pool_id': buy_pool_id,
                        'sell_pool_id': sell_pool_id,
                        'buy_pool_data': buy_pool,
                        'sell_pool_data': sell_pool,
                        'max_flow': max_flow,
                        'optimal_amount': feasible_amount,
                        'buy_unwrapped': buy_pool['unwrapped_crc'],
                        'sell_unwrapped': sell_pool['unwrapped_crc'],
                        'needs_trust': need_trust
                    }
                })

            # Return a "noop" so the simulation can continue
            return [
                ContractCall(
                    client_name="master",
                    method="noop",
                    params={"sender": sender}
                )
            ]

        except Exception as e:
            logger.error(f"Error in arbitrage check: {e}", exc_info=True)

        finally:
            # Always restore the original CirclesHub state
            context.network_state['contract_states']['CirclesHub']['state'] = original_hub_state
            context.rebuild_graph()

        # If we get here, return a noop
        return [
            ContractCall(
                client_name="master",
                method="noop",
                params={"sender": context.acting_address}
            )
        ]
    