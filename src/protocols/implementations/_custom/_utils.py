
from typing import Dict,  Tuple, List, Optional 
from src.framework.core.context import SimulationContext
from src.framework.logging import get_logger
import logging
import random

logger = get_logger(__name__,logging.INFO)



def _analyze_flow(context: SimulationContext, source: str, sink: str, cutoff: str = None) -> Tuple[int, list, Dict, Dict]:
        """Analyze flow between addresses"""
        

        try:
            if not context.graph_manager:
                logger.warning("No graph manager available - rebuilding")
                context.rebuild_graph()
                
                if not context.graph_manager:
                    logger.error("Failed to create graph manager")
                    return 0, [], {}, {}

            # Debug graph state
            logger.debug(f"Analyzing flow from {source} to {sink}")
            logger.debug(f"Graph has {context.graph_manager.graph.num_vertices()} vertices and "
                        f"{context.graph_manager.graph.num_edges()} edges")

            
            source_id = context.graph_manager.data_ingestion.get_id_for_address(source)
            sink_id = context.graph_manager.data_ingestion.get_id_for_address(sink)
            # Verify source and sink exist in graph
            if not context.graph_manager.graph.has_vertex(source_id):
                logger.warning(f"Source {source} not in graph")
                return 0, [], {}, {}
            if not context.graph_manager.graph.has_vertex(sink_id):
                logger.warning(f"Sink {sink} not in graph")
                return 0, [], {}, {}

            return context.graph_manager.analyze_flow(
                source=source,
                sink=sink,
                cutoff=cutoff
            )

        except Exception as e:
            logger.error(f"Flow analysis failed: {e}", exc_info=True)
            return 0, [], {}, {}
        
def _analyze_arbitrage(context: SimulationContext, source: str, start_token: str, end_token: str, cutoff: int) -> Tuple[int, list, Dict, Dict]:
    """Analyze flow between addresses"""
    try:
        if not context.graph_manager:
            logger.warning("No graph manager available - rebuilding")
            context.rebuild_graph()
            
            if not context.graph_manager:
                logger.error("Failed to create graph manager")
                return 0, [], {}, {}

        # Get IDs and log full details
        source_id = context.graph_manager.data_ingestion.get_id_for_address(source)
        start_token_id = context.graph_manager.data_ingestion.get_id_for_address(start_token)
        end_token_id = context.graph_manager.data_ingestion.get_id_for_address(end_token)
        
        logger.debug(f"Analyzing arbitrage flow:")
        logger.debug(f"Source: {source} -> ID: {source_id}")
        logger.debug(f"Start Token: {start_token} -> ID: {start_token_id}")
        logger.debug(f"End Token: {end_token} -> ID: {end_token_id}")

        # Debug graph state
        logger.debug(f"Graph has {context.graph_manager.graph.num_vertices()} vertices and "
                    f"{context.graph_manager.graph.num_edges()} edges")

        # Verify source exists in graph
        if not context.graph_manager.graph.has_vertex(source_id):
            logger.warning(f"Source {source} not in graph")
            return 0, [], {}, {}

        result = context.graph_manager.analyze_arbitrage(
            source=source,
            start_token=start_token,
            end_token=end_token,
            cutoff=cutoff
        )
        
        if not result[2]:  # If edge_flows is empty
            logger.debug("No edge flows found in arbitrage analysis")
        
        return result

    except Exception as e:
        logger.error(f"Arbitrage analysis failed: {e}", exc_info=True)
        return 0, [], {}, {}
        
def _analyze_arbitrage2(context: SimulationContext, source: str, start_token: str, end_token: str) -> Tuple[int, list, Dict, Dict]:
    """Analyze flow between addresses"""
    try:
        if not context.graph_manager:
            logger.warning("No graph manager available - rebuilding")
            context.rebuild_graph()
            
            if not context.graph_manager:
                logger.error("Failed to create graph manager")
                return 0, [], {}, {}

        # Get IDs and log full details
        source_id = context.graph_manager.data_ingestion.get_id_for_address(source)
        start_token_id = context.graph_manager.data_ingestion.get_id_for_address(start_token)
        end_token_id = context.graph_manager.data_ingestion.get_id_for_address(end_token)
        
        logger.debug(f"Analyzing arbitrage flow:")
        logger.debug(f"Source: {source} -> ID: {source_id}")
        logger.debug(f"Start Token: {start_token} -> ID: {start_token_id}")
        logger.debug(f"End Token: {end_token} -> ID: {end_token_id}")

        # Debug graph state
        logger.debug(f"Graph has {context.graph_manager.graph.num_vertices()} vertices and "
                    f"{context.graph_manager.graph.num_edges()} edges")

        # Verify source exists in graph
        if not context.graph_manager.graph.has_vertex(source_id):
            logger.warning(f"Source {source} not in graph")
            return 0, [], {}, {}

        result = context.graph_manager.analyze_arbitrage(
            source=source,
            start_token=start_token,
            end_token=end_token
        )
        
        if not result[2]:  # If edge_flows is empty
            logger.debug("No edge flows found in arbitrage analysis")
        
        return result

    except Exception as e:
        logger.error(f"Arbitrage analysis failed: {e}", exc_info=True)
        return 0, [], {}, {}
        


def _get_pool_reserves(context: SimulationContext, poolId: str) -> Tuple[List[str], List[int]]:
    """Get tokens and balances for a pool"""
    client = context.get_client("balancerv2vault")
    if not client:
        return [], []
    try:
        tokens, balances, _ = client.getPoolTokens(poolId)
        return tokens, balances
    except Exception as e:
        logger.error(f"Failed to get pool tokens: {e}")
        return [], []

def _find_arb_opportunity(
    pools_data: List[Dict],
    min_diff_threshold: float = 0.02,
    min_swap_threshold: int = 10**17
) -> Tuple[Optional[str], Optional[str], float, int]:
    """
    Find the best arbitrage opportunity among pools, factoring in actual
    swap feasibility. Each pool's 'price' is (backing_balance / crc_balance).

    Steps:
      1) For every pair of distinct pools (poolA, poolB), compare their prices.
         If 'priceA < priceB', we consider buying CRC in poolA and selling in poolB.
         Otherwise, buy in B and sell in A.
      2) Compute the recommended 'buy_amount' via `_calculate_optimal_swap_amount`
         for the chosen buy-pool (backing->CRC).
      3) Compute the 'sell_amount' for the chosen sell-pool (CRC->backing).
      4) The feasible trade size is min(buy_amount, sell_amount).
      5) If price difference < min_diff_threshold, skip.
      6) If feasible_amount < min_swap_threshold, skip.
      7) Keep track of the best difference across all feasible pairs.

    Returns:
      (buy_pool_id, sell_pool_id, best_diff, feasible_amount)

    If no feasible pair found, returns (None, None, 0.0, 0).
    """
    best_opportunity = (None, None, 0.0, 0)  # (buy_pool_id, sell_pool_id, diff, feasible_amount)

    # Edge case: Need at least 2 pools
    if len(pools_data) < 2:
        return (None, None, 0.0, 0)

    # We'll hold all equally good opportunities and choose randomly among them
    best_opportunities = []

    for i in range(len(pools_data)):
        poolA = pools_data[i]
        priceA = poolA['price']

        for j in range(i + 1, len(pools_data)):
            poolB = pools_data[j]
            priceB = poolB['price']

            # Avoid zero or negative prices
            if priceA <= 0 or priceB <= 0:
                continue

            # 1) Figure out which pool is "buy" vs. "sell"
            if priceA < priceB:
                # buy CRC in poolA, sell in poolB
                buy_pool = poolA
                sell_pool = poolB
                diff = priceB - priceA
            else:
                # buy in poolB, sell in poolA
                buy_pool = poolB
                sell_pool = poolA
                diff = priceA - priceB

            # 2) Check if price difference is above threshold
            if diff < min_diff_threshold:
                continue

            # 3) Compute recommended buy/sell amounts
            #    - buy_pool: supply backing, get CRC
            #    - sell_pool: supply CRC, get backing
            buy_amount = _calculate_optimal_swap_amount(
                buy_pool['tokens'],
                buy_pool['balances'],
                buy_pool['token_indices']['backing'],  # we supply backing
                buy_pool['token_indices']['crc']       # we receive CRC
            )
            sell_amount = _calculate_optimal_swap_amount(
                sell_pool['tokens'],
                sell_pool['balances'],
                sell_pool['token_indices']['crc'],     # we supply CRC
                sell_pool['token_indices']['backing']  # we receive backing
            )
            feasible_amount = min(buy_amount, sell_amount)

            # 4) Check if feasible amount is big enough
            if feasible_amount < min_swap_threshold:
                continue

            # 5) Keep track of the best difference
            current_best_diff = best_opportunity[2]
            if diff > current_best_diff:
                # Strictly bigger difference => reset
                best_opportunity = (buy_pool['id'], sell_pool['id'], diff, feasible_amount)
                best_opportunities = [best_opportunity]
            elif abs(diff - current_best_diff) < 1e-18:
                # Ties for the same difference => accumulate
                best_opportunities.append((buy_pool['id'], sell_pool['id'], diff, feasible_amount))

    # Finally pick a random top candidate from best_opportunities
    if best_opportunities:
        return random.choice(best_opportunities)
    else:
        return (None, None, 0.0, 0)
    
def _find_arb_opportunity2(pools_data: List[Dict]) -> Tuple[Optional[str], Optional[str], float]:
    """
    Find the best arbitrage opportunity between pools, where each pool's
    `price` is defined as (backing_balance / crc_balance).
    
    Returns:
      (buy_pool_id, sell_pool_id, price_difference)

    If price1 < price2, then CRC is cheaper in pool1: buy in pool1, sell in pool2.
    """
    best_opportunity = (None, None, 0.0)
    
    for i, pool1 in enumerate(pools_data):
        
        best_opportunities = []
        for j in range(i+1, len(pools_data)):
            pool2 = pools_data[j]
            price1 = pool1['price']  # backing / CRC
            price2 = pool2['price']  # backing / CRC
            diff = abs(price1 - price2)

            if diff > best_opportunity[2]:

                if price1 < price2:
                    # Cheaper to buy CRC in pool1, sell in pool2
                    best_opportunity = (pool1['id'], pool2['id'], price2 - price1)
                else:
                    # Cheaper to buy CRC in pool2, sell in pool1
                    best_opportunity = (pool2['id'], pool1['id'], price1 - price2)
                
                best_opportunities.append(best_opportunity)

    best_opportunity = random.choice(best_opportunities)
    return best_opportunity


def _calculate_optimal_swap_amount(
    tokens_in_pool: List[str],
    balances: List[int],
    token_in_idx: int,
    token_out_idx: int
) -> int:
    """
    Calculate a recommended swap amount considering Balancer’s recommended 30% max input ratio
    to avoid large price impacts or reverts. Expects the correct (token_in_idx, token_out_idx).

    Returns an integer of how many `token_in` units to swap.
    """
    try:
        balance_in = balances[token_in_idx]
        # Balancer typically sets a 'max in ratio' around 30% of the pool's 'in' balance.
        max_in_amount = int(balance_in * 0.1)
        # Use a safer fraction of that to avoid borderline reverts
        safe_amount = int(max_in_amount * 0.8)

        # If there's an edge-case or zero, ensure we don't go negative
        return max(safe_amount, 0)

    except Exception as e:
        logger.error(f"Error calculating optimal swap amount: {e}")
        return 0





