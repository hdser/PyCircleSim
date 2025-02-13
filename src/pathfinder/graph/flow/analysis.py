from typing import List, Tuple, Dict, Callable, Optional
from networkx.algorithms.flow import preflow_push
from collections import defaultdict

from ..base import BaseGraph
from .decomposition import simplify_paths

from src.framework.logging import get_logger
import logging

logger = get_logger(__name__,logging.INFO)

class NetworkFlowAnalysis:
    """Handle flow analysis for all graph implementations."""
    
    def __init__(self, graph: BaseGraph):
        self.graph = graph
        self.logger = logging.getLogger(__name__)


    def analyze_flow(self, source: str, sink: str, flow_func: Optional[Callable] = None, 
                    requested_flow: Optional[str] = None):
        """
        Analyze flow between source and sink nodes.
        
        Args:
            source: Source node ID
            sink: Sink node ID
            flow_func: Flow algorithm to use (optional)
            requested_flow: Maximum flow to compute (optional)
            
        Returns:
            Tuple containing:
            - Flow value
            - Simplified paths
            - Simplified edge flows
            - Original edge flows
        """
        # Get appropriate flow algorithm if none provided
        if flow_func is None:
            flow_func = self._get_default_algorithm()

        # Compute flow only once
        logger.debug(f"Computing flow from {source} to {sink}")
        if flow_func:
            logger.debug(f"Flow function: {flow_func.__name__}")
            
        flow_value, flow_dict = self.graph.compute_flow(
            source, 
            sink, 
            flow_func, 
            requested_flow
        )

        logger.debug(f"Raw flow computation returned: {flow_value}")
    
        # Before decomposition
        logger.debug(f"Flow into sink nodes:")
        sink_flows = sum(flows.get(sink, 0) for flows in flow_dict.values())
        logger.debug(f"Total sink flow from dictionary: {sink_flows}")

        # Decompose into paths
        paths, edge_flows = self.graph.flow_decomposition(
            flow_dict, 
            source, 
            sink, 
            int(requested_flow) if requested_flow else None
        )
        
        # Create simplified paths and edge flows
        simplified_paths = self.graph.simplified_flow_decomposition(paths)
        simplified_edge_flows = self._simplify_edge_flows(edge_flows)
        
        return flow_value, simplified_paths, simplified_edge_flows, edge_flows

    def _get_default_algorithm(self) -> Optional[Callable]:
        """Get default flow algorithm based on graph implementation."""
        graph_type = self._get_graph_type()
        if graph_type == 'networkx':
            return preflow_push
        return None  # OR-Tools uses its own algorithm

    def _get_graph_type(self) -> str:
        """Determine graph implementation type."""
        module_name = self.graph.__class__.__module__
        if 'networkx' in module_name:
            return 'networkx'
        return 'ortools'

    def _simplify_edge_flows(self, edge_flows: Dict[Tuple[str, str], int]) -> Dict[Tuple[str, str], Dict[str, int]]:
        """Group flows by token for each edge."""
        simplified = {}
        
        for (u, v), flow in edge_flows.items():
            # Skip virtual sink edges
            if v is not None and str(v).startswith('virtual_sink_'):
                continue
                
            # Convert intermediate node flows to token flows
            if '_' in str(u):
                real_u, token = str(u).split('_', 1)
                if (real_u, v) not in simplified:
                    simplified[(real_u, v)] = {}
                simplified[(real_u, v)][token] = (
                    simplified[(real_u, v)].get(token, 0) + flow
                )
                
        return simplified
    


    def analyze_arbitrage(self, start_node: str, start_token: str, end_token: str,  
                        flow_func: Optional[Callable] = None,
                        cutoff: Optional[int] = None) -> Tuple[int, List, Dict, Dict]:
        """Analyze arbitrage opportunities with optional cutoff."""
        try:
            source, virtual_sink = self.graph.prepare_arbitrage_graph(
                start_node, start_token, end_token
            )
            
            if source is None or virtual_sink is None:
                return 0, [], {}, {}

            # Pass cutoff directly to compute_flow
            flow_value, flow_dict = self.graph.compute_flow(
                source, 
                virtual_sink,
                flow_func,
                cutoff
            )
            
            if flow_value == 0:
                return 0, [], {}, {}
                    
            self.logger.debug(f"Found max flow: {flow_value}")
            # Pass cutoff to interpret_arbitrage_flow
            real_flow_dict = self.graph.interpret_arbitrage_flow(
                flow_dict, start_node, virtual_sink, cutoff
            )
            
            all_paths = self._find_all_flow_paths(flow_dict, source, virtual_sink)
            paths = []
            edge_flows = {}
            current_flow = 0
            
            for path, path_flow_value in all_paths:
                # Limit path flow by remaining cutoff
                if cutoff is not None:
                    path_flow_value = min(path_flow_value, cutoff - current_flow)
                    if path_flow_value <= 0:
                        continue

                real_path = path[:-1] + [source]
                tokens = []
                for node in real_path[1:-1]:
                    if '_' in node:
                        _, token = node.split('_')
                        tokens.append(token)
                
                for i in range(len(real_path)-1):
                    edge = (real_path[i], real_path[i+1])
                    edge_flows[edge] = edge_flows.get(edge, 0) + path_flow_value
                
                paths.append((real_path, tokens, path_flow_value))
                current_flow += path_flow_value
                
                if cutoff is not None and current_flow >= cutoff:
                    break
            
            if not paths:
                return flow_value, [], {}, {}
                
            simplified_paths = simplify_paths(paths)
            simplified_flows = self._simplify_edge_flows(edge_flows)
            
            return min(current_flow, cutoff) if cutoff else current_flow, simplified_paths, simplified_flows, edge_flows
                
        finally:
            self.graph.cleanup_arbitrage_graph()

    def analyze_arbitrage2(self, start_node: str, start_token: str, end_token: str,  
                     flow_func: Optional[Callable] = None) -> Tuple[int, List, Dict, Dict]:
        """Analyze arbitrage opportunities."""
        try:
            source, virtual_sink = self.graph.prepare_arbitrage_graph(
                start_node, start_token, end_token
            )
            
            if source is None or virtual_sink is None:
                return 0, [], {}, {}

            # Compute max flow
            flow_value, flow_dict = self.graph.compute_flow(
                source, 
                virtual_sink,
                flow_func
            )
            
            if flow_value == 0:
                return 0, [], {}, {}
                
            self.logger.debug(f"Found max flow: {flow_value}")

            self.logger.debug("flows")
            for end_pos, flows in flow_dict.items():
                if flows != {}:
                    self.logger.debug(f"{end_pos}: {flows}")
            
            # Find all possible paths to virtual sink
            all_paths = self._find_all_flow_paths(flow_dict, source, virtual_sink)
            
            paths = []
            edge_flows = {}
            
            # Process each path
            for path, path_flow_value in all_paths:
                # Complete cycle back to source
                real_path = path[:-1] + [source]  # Replace virtual_sink with source
                
                # Extract tokens from node IDs
                tokens = []
                for node in real_path[1:-1]:  # Skip first and last (source nodes)
                    if '_' in node:
                        _, token = node.split('_')
                        tokens.append(token)
                
                # Record flows
                for i in range(len(real_path)-1):
                    edge = (real_path[i], real_path[i+1])
                    edge_flows[edge] = edge_flows.get(edge, 0) + path_flow_value
                
                paths.append((real_path, tokens, path_flow_value))
            
            if not paths:
                return flow_value, [], {}, {}
                
            # Create simplified paths
            simplified_paths = simplify_paths(paths)
            simplified_flows = self._simplify_edge_flows(edge_flows)
            
            return flow_value, simplified_paths, simplified_flows, edge_flows
            
        finally:
            self.graph.cleanup_arbitrage_graph()

    def _find_flow_path(self, flow_dict: Dict[str, Dict[str, int]], source: str, 
                    target: str, final_flow: int) -> Optional[List[str]]:
        """
        Find a path from source to target with required flow using DFS.
        
        Args:
            flow_dict: Dictionary of flows {node: {neighbor: flow}}
            source: Starting node
            target: Target node to reach
            final_flow: Required minimum flow along path
        """
        path = [source]
        visited = {source}
        stack = [(source, list(flow_dict.get(source, {}).items()))]
        
        while stack:
            current, edges = stack[-1]
            
            if not edges:  # No more edges to explore from current node
                stack.pop()
                if path:
                    visited.remove(path.pop())
                continue
            
            next_node, flow = edges.pop()  # Try next edge
            
            if flow >= final_flow and next_node not in visited:
                path.append(next_node)
                
                if next_node == target:  # Found target
                    return path
                
                visited.add(next_node)
                next_edges = list(flow_dict.get(next_node, {}).items())
                if next_edges:  # If there are edges to explore from next_node
                    stack.append((next_node, next_edges))
                else:  # Dead end
                    visited.remove(next_node)
                    path.pop()
        
        return None

    def _find_all_flow_paths(self, flow_dict: Dict[str, Dict[str, int]], source: str, sink: str) -> List[Tuple[List[str], int]]:
        """
        Find all flow paths from source to sink.
        
        Args:
            flow_dict: Dictionary of flows
            source: Source node
            sink: Sink node
            
        Returns:
            List of (path, flow) tuples
        """
        paths = []
        
        # Create residual graph we can modify
        residual = defaultdict(dict)
        for u, flows in flow_dict.items():
            for v, flow in flows.items():
                if flow > 0:
                    residual[u][v] = flow
        
        # Keep finding paths until no more exist
        while True:
            # Find path with minimum flow along it
            path = []
            visited = {source}
            stack = [(source, list(residual[source].items()))]
            flows_to_node = {source: float('inf')}
            
            # DFS to find path
            while stack and not path:
                current, edges = stack[-1]
                
                if not edges:
                    stack.pop()
                    continue
                    
                next_node, flow = edges.pop()
                if flow > 0 and next_node not in visited:
                    visited.add(next_node)
                    flows_to_node[next_node] = min(flows_to_node[current], flow)
                    
                    if next_node == sink:
                        # Reconstruct path
                        path = self._reconstruct_path(source, sink, stack + [(next_node, [])])
                        min_flow = flows_to_node[sink]
                        paths.append((path, min_flow))
                        
                        # Update residual
                        for u, v in zip(path[:-1], path[1:]):
                            residual[u][v] -= min_flow
                            if residual[u][v] == 0:
                                del residual[u][v]
                    else:
                        stack.append((next_node, list(residual[next_node].items())))
            
            if not path:  # No more paths found
                break
                
        return paths

    def _reconstruct_path(self, source: str, sink: str, stack: List[Tuple[str, List]]) -> List[str]:
        """Helper to reconstruct path from DFS stack."""
        path = []
        nodes = [item[0] for item in stack]
        
        # Find path from source to sink
        for i, node in enumerate(nodes):
            path.append(node)
            if node == sink:
                break
                
        return path