
from typing import Dict,  Tuple 
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