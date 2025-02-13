import pandas as pd
from typing import Dict, Union, Tuple, Callable, List, Optional
import random
import time

from src.pathfinder.graph_loader import GraphLoader
from src.pathfinder.graph import GraphCreator, NetworkFlowAnalysis

from src.framework.logging import get_logger
import logging

logger = get_logger(__name__,logging.INFO)

class GraphManager:
    """
    Manages graph creation, analysis for network flow problems.
    
    Coordinates between different components:
    - Data ingestion (CSV or PostgreSQL)
    - Graph implementation (NetworkX, graph-tool, or OR-Tools)
    - Flow analysis
    """

    def __init__(self, data_source: Union[Tuple[str, str], Tuple[Dict[str, str], str]], 
                 graph_type: str = 'networkx'):
        """Initialize GraphManager with data source and graph implementation."""
        start = time.time()
        self.data_ingestion = self._initialize_data_ingestion(data_source)
        logger.debug(f"Ingestion time: {time.time()-start}")
        
        start = time.time()
        self.graph = GraphCreator.create_graph(
            graph_type, 
            self.data_ingestion.edges, 
            self.data_ingestion.capacities, 
            self.data_ingestion.tokens
        )
        logger.debug(f"Graph Creation time: {time.time()-start}")
        
        self.flow_analysis = NetworkFlowAnalysis(self.graph)

    def _initialize_data_ingestion(self, data_source):
        """Initialize the appropriate data ingestion based on the data source type."""
        if not isinstance(data_source, tuple) or len(data_source) != 2:
            raise ValueError("data_source must be a tuple with exactly 2 elements")

        try:
            df_trusts, df_balances = data_source
            return GraphLoader(df_trusts, df_balances)
        except Exception as e:
            raise ValueError(f"Error reading data")
        

    def analyze_flow(self, source: str, sink: str, flow_func=None, cutoff: str = None):
        """Analyze flow between source and sink nodes."""
        source_id = self.data_ingestion.get_id_for_address(source)
        sink_id = self.data_ingestion.get_id_for_address(sink)
        
        if source_id is None or sink_id is None:
            raise ValueError(f"Source address '{source}' or sink address '{sink}' not found in the graph.")
        
        if not self.graph.has_vertex(source_id) or not self.graph.has_vertex(sink_id):
            raise ValueError(f"Source node '{source_id}' or sink node '{sink_id}' not in graph.")
        
        return self.flow_analysis.analyze_flow(source_id, sink_id, flow_func, cutoff)

    
    def get_node_info(self):
        """Get information about nodes in the graph."""
        try:
            total_nodes = self.graph.num_vertices()
            total_edges = self.graph.num_edges()
            
            # Sample some nodes for display
            sample_nodes = random.sample(
                list(self.graph.get_vertices()), 
                min(5, self.graph.num_vertices())
            )
            sample_info = []
            
            for node in sample_nodes:
                if '_' in str(node):
                    sample_info.append(f"Intermediate Node: {node}")
                else:
                    address = self.data_ingestion.get_address_for_id(str(node))
                    sample_info.append(f"Node ID: {node}, Address: {address}")
                    
            return (f"Total nodes: {total_nodes}\n"
                    f"Total edges: {total_edges}\n"
                    f"Sample nodes:\n" + 
                    "\n".join(sample_info))
                    
        except Exception as e:
            return f"Error getting node info: {str(e)}"
    

    def analyze_arbitrage(self, source: str, start_token: str, end_token: str,
                        flow_func: Optional[Callable] = None,
                        cutoff: Optional[int] = None) -> Tuple[int, List, Dict, Dict]:
        """
        Find arbitrage opportunities using max flow.
        
        Args:
            source: Address of source/target node
            start_token: Address of token to start with
            end_token: Address of token to end with
            flow_func: Optional flow algorithm to use
            cutoff: Optional maximum flow limit
            
        Returns:
            Tuple containing:
            - Total flow value
            - Simplified paths
            - Simplified edge flows
            - Original edge flows
        """
        # Convert addresses to internal IDs
        source_id = self.data_ingestion.get_id_for_address(source)
        start_token_id = self.data_ingestion.get_id_for_address(start_token)
        end_token_id = self.data_ingestion.get_id_for_address(end_token)
        
        if not all([source_id, start_token_id, end_token_id]):
            raise ValueError("Invalid addresses provided")
            
        # Run arbitrage analysis with cutoff
        results = self.flow_analysis.analyze_arbitrage(
            source_id,
            start_token_id,
            end_token_id,
            flow_func,
            cutoff
        )
        
        return results