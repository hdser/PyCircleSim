
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
        
def _analyze_arbitrage(context: SimulationContext, source: str, start_token: str, end_token: str) -> Tuple[int, list, Dict, Dict]:
        """Analyze flow between addresses"""
        
        try:
            if not context.graph_manager:
                logger.warning("No graph manager available - rebuilding")
                context.rebuild_graph()
                
                if not context.graph_manager:
                    logger.error("Failed to create graph manager")
                    return 0, [], {}, {}

            # Debug graph state
            logger.debug(f"Graph has {context.graph_manager.graph.num_vertices()} vertices and "
                        f"{context.graph_manager.graph.num_edges()} edges")

            
            source_id = context.graph_manager.data_ingestion.get_id_for_address(source)
            # Verify source and sink exist in graph
            if not context.graph_manager.graph.has_vertex(source_id):
                logger.warning(f"Source {source} not in graph")
                return 0, [], {}, {}



            return context.graph_manager.analyze_arbitrage(
                source=source,
                start_token=start_token,
                end_token=end_token
            )

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
    Find the best arbitrage opportunity between pools
    Returns: (buy_pool_id, sell_pool_id, price_difference)
    """
    best_opportunity = (None, None, 0.0)
    
    for i, pool1 in enumerate(pools_data):
        for j, pool2 in enumerate(pools_data):
            if i >= j:
                continue
                
            price1 = pool1['balances'][1] / pool1['balances'][0] 
            price2 = pool2['balances'][1] / pool2['balances'][0]
            
            price_diff = abs(price1 - price2)
            if price_diff > best_opportunity[2]:
                if price1 < price2:
                    best_opportunity = (pool1['id'], pool2['id'], price_diff)
                else:
                    best_opportunity = (pool2['id'], pool1['id'], price_diff)
                    
    return best_opportunity