
from typing import Dict,  Tuple, List, Optional 
from src.framework.core.context import SimulationContext
from src.framework.logging import get_logger
import logging

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


def _find_arb_opportunity(pools_data: List[Dict]) -> Tuple[Optional[str], Optional[str], float]:
    """
    Find the best arbitrage opportunity between pools, where each pool's
    `price` is defined as (backing_balance / crc_balance).
    
    Returns:
      (buy_pool_id, sell_pool_id, price_difference)

    If price1 < price2, then CRC is cheaper in pool1: buy in pool1, sell in pool2.
    """
    best_opportunity = (None, None, 0.0)
    
    for i, pool1 in enumerate(pools_data):
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
        max_in_amount = int(balance_in * 0.3)
        # Use a safer fraction of that to avoid borderline reverts
        safe_amount = int(max_in_amount * 0.8)

        # If there's an edge-case or zero, ensure we don't go negative
        return max(safe_amount, 0)

    except Exception as e:
        logger.error(f"Error calculating optimal swap amount: {e}")
        return 0





