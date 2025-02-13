
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
        2) Identify which token is CRC vs. backing. We'll compute price = (backing_balance / crc_balance).
        3) Use `_find_arb_opportunity` to see if there's a sufficient difference.
        4) If found, do a test flow with artificially added balance & trust to see if path is feasible.
        5) Save that info into `context` for next steps in the sequence.
        6) Always restore any state modifications before returning.

        Returns empty (a 'noop') if no opportunity or after storing info in `context`.
        """
        # For robust error handling and final state restoration
        original_hub_state = copy.deepcopy(context.network_state['contract_states']['CirclesHub']['state'])
        try:
            sender = context.acting_address

            # 1. Collect LBP pools
            if (
                'BalancerV2LBPFactory' not in context.network_state['contract_states'] or
                'LBPs' not in context.network_state['contract_states']['BalancerV2LBPFactory']['state']
            ):
                logger.info("No LBP pools in state.")
                return []

            LBPs_state = context.network_state['contract_states']['BalancerV2LBPFactory']['state']['LBPs']
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

            # 2. Build up a list of pools_data with consistent price
            pools_data = []
            for poolId, pool_info in LBPs_state.items():
                try:
                    tokens = pool_info['tokens']
                    balances = balancer_vault.getPoolTokens(poolId)[1]  # second return is the balances array

                    # Identify CRC vs. backing
                    crc_token = None
                    unwrapped_crc = None
                    backing_token = None
                    for t in tokens:
                        # If it has an avatar => it's a CRC wrapper
                        try:
                            avatar_addr = client_demurrage.avatar(t)
                            if avatar_addr:
                                crc_token = t
                                unwrapped_crc = avatar_addr
                            else:
                                backing_token = t
                        except:
                            # Not a CRC wrapper => treat as backing
                            backing_token = t

                    if not (crc_token and backing_token):
                        continue

                    crc_idx = tokens.index(crc_token)
                    backing_idx = tokens.index(backing_token)
                    crc_balance = balances[crc_idx]
                    backing_balance = balances[backing_idx]

                    # Avoid division by zero
                    if crc_balance <= 0:
                        continue

                    price = backing_balance / float(crc_balance)  # backing / CRC

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

            # If fewer than 2 pools, no cross-pool arb possible
            if len(pools_data) < 2:
                logger.info("Fewer than 2 LBP pools, cannot arbitrage.")
                return []

            # 3. Find potential arbitrage
            buy_pool_id, sell_pool_id, price_diff = _find_arb_opportunity(pools_data)
            if not buy_pool_id or price_diff < 0.02:  # requiring at least 2% difference
                logger.info(f"No arbitrage found above threshold. Best diff was {price_diff}.")
                return []

            # Identify the chosen pools
            buy_pool = next(p for p in pools_data if p['id'] == buy_pool_id)
            sell_pool = next(p for p in pools_data if p['id'] == sell_pool_id)

            # 4. Calculate how much to buy / sell (max_in ratio logic)
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
            optimal_amount = min(buy_amount, sell_amount)
            logger.info(f"Potential buy_amount={buy_amount}, sell_amount={sell_amount}, using {optimal_amount}.")

            if optimal_amount <= 1e18:
                logger.info("Optimal buy/sell amount is too small or zero.")
                return []

            # 5. Simulate a large test balance & trust to confirm path
            #    We'll artificially set the sender's balance in buy_pool['unwrapped_crc']
            #    to a large number, then confirm there's a flow from unwrapped buy token
            #    to unwrapped sell token.
            test_amount = 9e30  # big test amount
            hub_state = context.network_state['contract_states']['CirclesHub']['state']
            if 'token_balances' not in hub_state:
                hub_state['token_balances'] = {}
            if sender not in hub_state['token_balances']:
                hub_state['token_balances'][sender] = {}

            # Insert test balance
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
                # set an expiry well in the future for simulation
                hub_state['trustMarkers'][sender][sell_pool['unwrapped_crc']] = (
                    context.chain.blocks.head.timestamp + 365 * 24 * 60 * 60
                )

            # Rebuild graph after modifications
            context.rebuild_graph()

            # Check if we can now flow from buy_unwrapped -> sell_unwrapped
            max_flow, _, edge_flows, _ = _analyze_arbitrage(
                context,
                sender,
                buy_pool['unwrapped_crc'],
                sell_pool['unwrapped_crc'],
                None
            )

            # Revert hub state
            context.network_state['contract_states']['CirclesHub']['state'] = original_hub_state
            context.rebuild_graph()

            if max_flow > 0:
                logger.info(f"Found feasible path with flow={max_flow}. Price diff={price_diff}")
                # Save details for next steps in the sequence
                context.update_running_state({
                    'arb_check': {
                        'buy_pool_id': buy_pool_id,
                        'sell_pool_id': sell_pool_id,
                        'buy_pool_data': buy_pool,
                        'sell_pool_data': sell_pool,
                        'max_flow': max_flow,
                        'optimal_amount': optimal_amount,
                        'buy_unwrapped': buy_pool['unwrapped_crc'],
                        'sell_unwrapped': sell_pool['unwrapped_crc'],
                        'needs_trust': need_trust
                    }
                })

            # Return an empty call just to let the script continue
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

        return [
            ContractCall(
                client_name="master",
                method="noop",
                params={"sender": context.acting_address}
            )
        ]